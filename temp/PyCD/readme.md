# PyCD: Extracting dependency relations from dependency configuration  files
To use PyCD, you can run the command:
```
python3 GetDep_ast.py <pro_path> <tofile>
```
- *pro_path* refers to the path for a Python project or a configuration file.
- *tofile* refers to a **.csv** file that store the dependencies PyCD has extracted, such as 'result.csv'

PyCD supports the parsing for three common configuration files used in Python projects.
- setup.py
- requirements.txt.
- Pipfile

<!-- And it is easy to add other configuration files. -->

要使用PyCD工具，你可以运行以下命令：

shell

```shell
python3 GetDep_ast.py <pro_path> <tofile>
```

- `<pro_path>` 指的是一个Python项目的路径或者一个配置文件的路径。
- `<tofile>` 指的是一个**.csv**文件，用于存储PyCD提取的依赖关系，例如 `'result.csv'`。

PyCD支持解析Python项目中常用的三种配置文件：

1. `setup.py`：这是一个特殊的Python脚本，用于定义包的元数据和依赖关系。
2. `requirements.txt`：这是一个纯文本文件，列出了项目的依赖及其版本要求。
3. `Pipfile`：这是Pipenv工具使用的文件，用于定义项目的依赖关系，支持更复杂的依赖管理功能，如版本锁定。

使用PyCD可以帮助开发者更准确地提取和分析Python项目的依赖信息，从而更好地管理和维护项目的依赖关系