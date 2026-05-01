# Changelog

---

## [0.1.0] - 2026-4-16

### Added 2026-4-16 (1)

- Initial release of the dilicom-parser package.

---

## [0.1.1] - 2026-4-16

### Added 2026-4-16 (2)

- Added functionality to parse EANCOD and GENCODE from Dilicom data.

### Fixed 2026-4-16 (1)

- Fixed problem of publisher code.

---

## [0.1.2] - 2026-4-16

### Fixed 2026-4-16 (2)

- Fixed problem of crash due of import problem.

---

## [0.2.0] - 2026-4-16

### Added 2026-4-16 (3)

- Added functionality to connect to the Dilicom SFTP server and retrieve data.

## [0.2.1] - 2026-4-17

### Added 2026-4-17 (1)

- Added functionality to download all items of a specific folder from the Dilicom SFTP server.

### Fixed 2026-4-17 (1)

- Problem during distributors file parsing fixed.
- Problem to add a specific env file during Connector initialization fixed.
- Using the folder of the .env file to download the files from the SFTP server fixed.

## [0.2.2] - 2026-4-17

### Fixed 2026-4-17 (2)

- Accept used with Python 3.14+ fixed.

## [0.2.3] - 2026-4-17

### Fixed 2026-4-17 (3)

- Problem with parsing distributors files if complete path is given fixed.

## [0.2.4] - 2026-4-20

### Added 2026-4-20 (1)

- Change logic for verifying file type using a clasifier instead of using a method in the parser. This allows to separate the concerns and to have a more flexible architecture for future extensions. The classifier is now responsible for determining the type of each file, using a dictionary with keys = strings to search in the header of the file and values = the corresponding class object to use for parsing. The parser can now parse many files of same type in a single call and the classifier can easily give to each parser the correct list of files to parse in a single call.

## [0.2.5] - 2026-4-20

### Added 2026-4-20 (2)

- Added a parse method in the classifier to call the parse method of each parser with the list of files of the corresponding type. This allows to have a single entry point for parsing all the files, and to get a dictionary with keys = file types and values = lists of parsed objects for each type.

## [0.2.6] - 2026-4-21

### Fixed 2026-4-21 (1)

- Problem TypeError: type 'Series' is not subscriptable fixed by added

    ```python
    from __future__ import annotations
    ```

## [0.2.7] - 2026-4-21

### Fixed 2026-4-21 (2)

- Problem of parsing distributors files fixed by changing the condition to check if the file is a distributor file in the classifier. The condition now checks if "Distrib_DLC" is in the header type_file instead of checking if it starts with "Distrib_DLC". This allows to correctly identify distributor files even if they have a complete path in the header.

## [0.2.8] - 2026-4-24

### Fixed 2026-4-24 (1)

- Problem of ignoring files with unrecognized header or encoding fixed by catching only ValueError exceptions instead of also UnicodeDecodeError exceptions. This allows to correctly ignore files with unrecognized header or encoding without crashing the program due to UnicodeDecodeError exceptions.

## [0.2.9] - 2026-5-1

### Added 2026-5-1 (1)

- Add solution to parse ONIX files with onixlib. This allows to have a more robust and complete parsing of ONIX files, with support for all the features and variations of the ONIX format, and to get a structured representation of the ONIX data as Python objects.
- Add example of usage in the README.md file for parsing ONIX files with onixlib. This allows to show how to use the new functionality for parsing ONIX files with onixlib, and to provide a clear and practical example for users who want to parse ONIX files with the dilicom-parser package.
- Add onixlib to the dependencies in the pyproject.toml file. This allows to ensure that onixlib is installed when installing the dilicom-parser package, and to avoid import errors when using the functionality for parsing ONIX files with onixlib.
- Add tests for parsing ONIX files with onixlib. This allows to verify that the new functionality for parsing ONIX files with onixlib works correctly, and to ensure the quality and reliability of the code for parsing ONIX files with onixlib in the dilicom-parser package.
- Add type hints for the new functionality for parsing ONIX files with onixlib. This allows to improve the readability and maintainability of the code for parsing ONIX files with onixlib, and to provide better support for type checking and code completion when using the functionality for parsing ONIX files with onixlib in the dilicom-parser package.
- Add documentation for the new functionality for parsing ONIX files with onixlib in the README.md file. This allows to provide clear and comprehensive documentation for users who want to use the functionality for parsing ONIX files with onixlib, and to explain the features and benefits of using onixlib for parsing ONIX files in the dilicom-parser package.
- Use of a streaming option in the classifier to parse large files without loading them entirely into memory. This allows to handle large files more efficiently and to avoid memory issues when parsing large files with the dilicom-parser package. The streaming option is implemented by using generators to read and parse the files line by line, instead of reading the entire file into memory at once. This allows to process large files in a more memory-efficient way, and to improve the performance of the parsing process for large files in the dilicom-parser package.
- The streaming option is automatically enabled when only one file is bigger than 512MB. This allows to optimize the parsing process for large files without requiring the user to manually enable the streaming option, and to ensure that large files are parsed efficiently without causing memory issues in the dilicom-parser package.
