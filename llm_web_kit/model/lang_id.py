import os
import re
import fasttext

from typing import Tuple
from llm_web_kit.libs.logger import mylogger as logger
from llm_web_kit.config.cfg_reader import get_config
from llm_web_kit.model.resource_utils.download_assets import (
    CACHE_DIR,
    download_auto_file,
)
from llm_web_kit.model.resource_utils.singleton_resource_manager import (
    singleton_resource_manager,
)


class LanguageIdentification:
    """
    Language Identification model using fasttext

    """

    def __init__(self, model_path: str = None):
        """
        Initialize LanguageIdentification model
        Will download the 176.bin model if model_path is not provided

        Args:
            model_path (str, optional): Path to the model. Defaults to None.
        """

        if not model_path:
            model_path = self.auto_download()
        self.model = fasttext.load_model(model_path)

    def auto_download(self):
        """
        Default download the 176.bin model
        """
        resource_name = "lang-id-176"
        resource_config = get_config()["resources"]
        lang_id_176_config: dict = resource_config[resource_name]
        lang_id_176_url = lang_id_176_config["download_path"]
        lang_id_176_md5 = lang_id_176_config.get("md5", "")
        target_path = os.path.join(CACHE_DIR, resource_name, "model.bin")
        logger.info(f"try to make target_path: {target_path} exist")
        target_path = download_auto_file(lang_id_176_url, target_path, lang_id_176_md5)
        logger.info(f"target_path: {target_path} exist")
        return target_path

    @property
    def version(self) -> str:
        """
        Get the version of the model
        The version is determined by the number of labels in the model
        now have 176 version from : https://fasttext.cc/docs/en/language-identification.html
        and 218 version from : https://huggingface.co/facebook/fasttext-language-identification/tree/main

        Returns:
            str: The version of the model
        """
        if not hasattr(self, "_version"):
            labels_num = len(self.model.get_labels())
            if labels_num == 176:
                self._version = "176.bin"
            elif labels_num == 218:
                self._version = "218.bin"
            else:
                raise ValueError(f"Unsupported version: {labels_num} labels")
        return self._version

    def predict(self, text: str, k: int = 5) -> Tuple[Tuple[str], Tuple[float]]:
        """
        Predict language of the given text
        Return first k predictions, if k is greater than number of predictions, return all predictions
        default k is 5

        Args:
            text (str): Text to predict language
            k (int, optional): Number of predictions to return. Defaults to 5.

        Returns:
            Tuple[Tuple[str], Tuple[float]]: Tuple of predictions and probabilities only return top 5 predictions
        """
        assert k > 0, "k should be greater than 0"

        # remove new lines
        text = text.replace("\n", " ")

        # returns top k predictions
        predictions, probabilities = self.model.predict(text, k=k)

        return predictions, probabilities


def get_singleton_lang_detect() -> LanguageIdentification:
    """
    Get the singleton language identification model

    returns:
        LanguageIdentification: The language identification model
    """
    if not singleton_resource_manager.has_name("lang_detect"):
        singleton_resource_manager.set_resource("lang_detect", LanguageIdentification())
    return singleton_resource_manager.get_resource("lang_detect")


def decide_language_by_prob_v176(
    predictions: Tuple[str], probabilities: Tuple[float]
) -> str:
    """
    Decide language based on probabilities
    The rules are tuned by Some sepciific data sources
    This is a fixed version for fasttext 176 model


    Args:
        predictions (Tuple[str]): the predicted languages labels by 176.bin model (__label__zh, __label__en, etc)
        probabilities (Tuple[float]): the probabilities of the predicted languages

    Returns:
        str: the final language label
    """
    lang_prob_dict = {}
    for lang_key, lang_prob in zip(predictions, probabilities):
        lang = lang_key.replace("__label__", "")
        lang_prob_dict[lang] = lang_prob

    zh_prob = lang_prob_dict.get("zh", 0)
    en_prob = lang_prob_dict.get("en", 0)
    zh_en_prob = zh_prob + en_prob
    final_lang = None
    if zh_en_prob > 0.5:
        if zh_prob > 0.4 * zh_en_prob:
            final_lang = "zh"
        else:
            final_lang = "en"
    else:
        if max(lang_prob_dict.values()) > 0.6:
            final_lang = max(lang_prob_dict, key=lang_prob_dict.get)
            if final_lang == "hr":
                final_lang = "sr"
        elif max(lang_prob_dict.values()) > 0 and max(
            lang_prob_dict, key=lang_prob_dict.get
        ) in ["sr", "hr"]:
            final_lang = "sr"
        else:
            final_lang = "mix"
    return final_lang


LANG_ID_SUPPORTED_VERSIONS = ["176.bin"]


def detect_code_block(content_str: str) -> bool:
    """
    Detect if the content string contains code block
    """
    code_hint_lines = sum(
        [1 for line in content_str.split("\n") if line.strip().startswith("```")]
    )
    return code_hint_lines > 1


def detect_inline_equation(content_str: str) -> bool:
    """
    Detect if the content string contains inline equation
    """
    inline_eq_pattern = re.compile(r"\$\$.*\$\$|\$.*\$")
    return any([inline_eq_pattern.search(line) for line in content_str.split("\n")])


def detect_latex_env(content_str: str) -> bool:
    """
    Detect if the content string contains latex environment
    """
    latex_env_pattern = re.compile(r"\\begin\{.*?\}.*\\end\{.*\}", re.DOTALL)
    return latex_env_pattern.search(content_str) is not None


def decide_language_func(content_str: str, lang_detect: LanguageIdentification) -> str:
    """
    Decide language based on the content string.
    This function will truncate the content string if it is too long.
    This function will return "empty" if the content string is empty.

    Raises:
        ValueError: Unsupported version.
            The prediction str is different for different versions of fasttext model.
            So the version should be specified.
            Now only support version "176.bin"

    Warning:
        The too long content string may be truncated.
        Some text with massive code block and equations may be misclassified.

    Args:
        content_str (str): The content string to decide language
        lang_detect (LanguageIdentification): The language identification model

    Returns:
        str: The final language label
    """

    # truncate the content string if it is too long
    str_len = len(content_str)
    if str_len > 10000:
        logger.warning("Content string is too long, truncate to 10000 characters")
        start_idx = (str_len - 10000) // 2
        content_str = content_str[start_idx : start_idx + 10000]

    # check if the content string contains code block, inline equation, latex environment
    if detect_code_block(content_str):
        logger.warning("Content string contains code block, may be misclassified")
    if detect_inline_equation(content_str):
        logger.warning("Content string contains inline equation, may be misclassified")
    if detect_latex_env(content_str):
        logger.warning(
            "Content string contains latex environment, may be misclassified"
        )

    # return "empty" if the content string is empty
    if len(content_str.strip()) == 0:
        return "empty"

    if lang_detect.version == "176.bin":
        predictions, probabilities = lang_detect.predict(content_str)
        result = decide_language_by_prob_v176(predictions, probabilities)
    else:
        raise ValueError(
            f"Unsupported version: {lang_detect.version}. Supported versions: {LANG_ID_SUPPORTED_VERSIONS}"
        )
    return result


def decide_lang_by_str(content_str: str) -> str:
    """
    Decide language based on the content string, based on decide_language_func
    """
    lang_detect = get_singleton_lang_detect()

    return decide_language_func(content_str, lang_detect)


def update_language_by_str(content_str: str) -> str:
    """
    Decide language based on the content string, based on decide_language_func
    """
    return {"language": decide_lang_by_str(content_str)}


if __name__ == "__main__":
    li = LanguageIdentification()
    print(li.version)
    text = "hello world, this is a test. the language is english"
    predictions, probabilities = li.predict(text)
    print(predictions, probabilities)

    print(update_language_by_str(text))

    text = "你好，这是一个测试。这个语言是中文"
    print(update_language_by_str(text))

    text = "```python\nprint('hello world')\n``` 这是一个中文的文档，包含了一些代码"
    print(update_language_by_str(text))

    text = "$$x^2 + y^2 = 1$$ これは数式を含むテストドキュメントです"
    print(update_language_by_str(text))

    text = "\\begin{equation}\n x^2 + y^2 = 1 \n\\end{equation} This is a test document, including some math equations"
    print(update_language_by_str(text))
