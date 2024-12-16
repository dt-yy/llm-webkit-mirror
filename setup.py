from setuptools import find_packages, setup


def parse_requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    requires = []

    for line in lines:
        if 'http' in line:
            pkg_name_without_url = line.split('@')[0].strip()
            requires.append(pkg_name_without_url)
        else:
            requires.append(line)

    return requires


setup(
    name='llm_web_kit',
    version='0.1.0',  # 版本号
    description='LLM Web Kit for processing and managing web content',
    packages=find_packages(exclude=['tests*']),
    install_requires=parse_requirements('requirements/runtime.txt'),  # 项目依赖的第三方库
    extras_require={
        'dev': parse_requirements('requirements/dev.txt'),
    },
    python_requires='>=3.10',
)
