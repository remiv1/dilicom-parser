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
