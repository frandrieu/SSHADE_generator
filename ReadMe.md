# SSHADE XML Generator GUI

## Overview
This project provides a graphical user interface (GUI) for editing and generating XML files for SSHADE using Python's `tkinter` library. The application allows users to load XML templates, edit values, add or remove elements, and save the modified XML file.

## Features
- **Load XML Files**: Open and edit existing XML files.
- **Load Templates**: Select from predefined XML templates.
- **Dynamic UI Generation**: The UI automatically builds form fields based on the XML structure.
- **Collapsible Sections**: Nested XML elements can be expanded or collapsed.
- **Mandatory Fields & Comments**: Highlights required fields and displays helpful comments.
- **Dropdown Selection**: Supports predefined enumeration options.
- **Add & Remove Elements**: Duplicate or delete elements dynamically.
- **Save XML Files**: Export the modified XML structure to a file.

## Installation
### Requirements
Ensure you have Python installed (>=3.6) along with `tkinter` (included in standard Python distribution).

### Clone the Repository
```bash
git clone https://github.com/frandrieu/SSHADE_generator.git
cd SSHADE_generator
```

### Run the Application
```bash
python SSHADE_XML_editor.py
```

## Usage
1. **Start the Application**
   - Run `python SSHADE_XML_editor.py` to launch the GUI.
2. **Load an existing XML File**
   - Click the "Load XML" button to open an existing XML file.
3. **Use a Template**
   - Click "Load Template" and select a predefined template.
4. **Edit XML Fields**
   - Modify the values in the dynamically generated form.
5. **Expand/Collapse Sections**
   - Click the ▶ or ▼ buttons to show or hide nested elements.
6. **Add or Remove Elements**
   - Click "+ Add" or "- Remove" for elements that support duplication.
7. **Save Your Work**
   - Click "Save As..." to store the modified XML file.

## File Structure
```
SSHADE_generator/
│── templates/                # Predefined XML templates
│── SSHADE_XML_editor.py      # Main application script
│── README.md                 # Project documentation
```

## Contributing
Feel free to fork the repository, make improvements, and submit a pull request!

## License
This project is licensed under CC-BY-SA licence

