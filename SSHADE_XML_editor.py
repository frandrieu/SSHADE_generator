#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 12:08:39 2025

Purpose:
    Charge and auto-fill an XML file for SSHADE
    Allows for changes in the file, with open fields and roll menus
    Export modified XML file
@author: fandrieu
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import copy
import uuid

class CollapsibleFrame:
    def __init__(self, parent, text, is_open=False):
        self.parent = parent
        self.is_open = is_open
        self.frame = ttk.Frame(parent)

        self.header = ttk.Frame(self.frame)
        self.toggle_btn = ttk.Button(
            self.header, text='▼' if is_open else '▶',
            width=2, command=self.toggle
        )
        self.toggle_btn.pack(side="left")
        ttk.Label(self.header, text=text).pack(side="left")
        self.header.pack(fill="x", anchor="w")

        self.content = ttk.Frame(self.frame)
        if is_open:
            self.content.pack(fill="x", expand=True)

    def toggle(self):
        self.is_open = not self.is_open
        self.toggle_btn.config(text='▼' if self.is_open else '▶')
        if self.is_open:
            self.content.pack(fill="x", expand=True)
        else:
            self.content.pack_forget()

class XMLGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Editor")
        self.root.geometry("1000x800")

        self.elements = []
        self.entries = {}
        self.original_lines = []
        self.file_path = None
        self.xml_structure = []

        # Main container
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)

        # Canvas and scrollbar
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = ttk.Scrollbar(
            self.container, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Controls
        control_frame = ttk.Frame(root)
        control_frame.pack(fill="x", pady=5)
        ttk.Button(control_frame, text="Load XML", command=self.load_xml).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Load Template", command=self.show_template_options).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Save As...", command=self.save_xml_as).pack(side="left", padx=5)

    def show_template_options(self):
        template_window = tk.Toplevel(self.root)
        template_window.title("Select Template")

        templates = [
            "database", "experiment", "experimentalist",
            "instrument", "laboratory", "matter",
            "publication", "sample"
        ]

        for template in templates:
            btn = ttk.Button(template_window, text=template,
                           command=lambda t=template: [self.load_template(t), template_window.destroy()])
            btn.pack(fill="x", padx=10, pady=2)

    def load_template(self, template_name):
        self.file_path = f"templates/template_{template_name}_commented_v092a.xml"
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.original_lines = file.readlines()
            self.process_xml()
            self.build_gui()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Template file {self.file_path} not found.")

    def load_xml(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if not self.file_path:
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            self.original_lines = file.readlines()

        self.process_xml()
        self.build_gui()

    def process_xml(self):
        self.xml_structure = []
        current_hierarchy = []
        current_label = None
        parent_stack = []

        for line_num, line in enumerate(self.original_lines):
            line = line.rstrip()  # Preserve the original indentation
            if not line:
                continue

            # Handle comments
            if line.startswith('<!--'):
                self.xml_structure.append({'type': 'comment', 'comment': line})
                continue

            # Parse XML elements
            element_part = line.split('<!--')[0].strip()
            comment_part = line.split('<!--')[1].strip() if '<!--' in line else ''

            if element_part.startswith('<') and element_part.endswith('>'):
                # Calculate depth based on original indentation
                original_indent = len(line) - len(line.lstrip())
                depth = original_indent // 2

                # Maintain hierarchy
                while parent_stack and parent_stack[-1]['depth'] >= depth:
                    parent_stack.pop()

                # Extract tag and value
                if element_part.startswith('</'):
                    continue  # Skip closing tags
                elif '>' in element_part:
                    tag_start = element_part.find('<') + 1
                    tag_end = element_part.find('>')
                    tag = element_part[tag_start:tag_end]
                    value = element_part[tag_end+1:element_part.find('</')].strip()
                else:
                    tag = element_part[1:-1]
                    value = ''

                element_info = {
                    'type': 'element',
                    'tag': tag,
                    'value': value,
                    'depth': depth,
                    'indent': ' ' * original_indent,
                    'mandatory': '**ABS MANDATORY**' in comment_part,
                    'enum_options': self.extract_enum_options(comment_part),
                    'children': [],
                    'label': current_label or tag,
                    'multiple': 'multiple' in comment_part,
                    'parent': parent_stack[-1] if parent_stack else None,
                    'comment': comment_part,
                    'raw': line,
                    'id': str(uuid.uuid4())  # Unique identifier for each element
                }
                current_label = None

                if parent_stack:
                    parent_stack[-1]['children'].append(element_info)
                else:
                    self.xml_structure.append(element_info)

                if not element_part.endswith('/>'):
                    parent_stack.append(element_info)

    def extract_enum_options(self, comment):
        enum_match = re.search(r'[Ee]num[:\s]*{([^}]+)}', comment)
        return [opt.strip() for opt in enum_match.group(1).split(',')] if enum_match else []

    def build_gui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        for element in self.xml_structure:
            if element['type'] == 'element':
                self.create_widget(element, self.scrollable_frame)
            elif element['type'] == 'comment':
                ttk.Label(self.scrollable_frame, text=element['comment'], wraplength=400, justify="left").pack(fill="x", anchor="w", pady=2)

    def create_widget(self, element, parent_frame, depth=0):
        has_children = len(element['children']) > 0
        indent = 20 * element['depth']

        frame_container = ttk.Frame(parent_frame)
        frame_container.pack(fill="x", anchor="w", pady=2)

        if has_children:
            frame = CollapsibleFrame(frame_container, element['tag'], is_open=True)
            frame.frame.pack(fill="x", anchor="w")
            input_container = frame.content
        else:
            input_container = frame_container

        # Create input field or container
        if not has_children:
            input_frame = ttk.Frame(input_container)
            input_frame.pack(fill="x", padx=(indent + 5, 0), pady=2)

            # Add label above the field
            ttk.Label(input_frame, text=element['tag']).pack(side="left")

            var = tk.StringVar(value=element['value'])

            if element['mandatory']:
                ttk.Label(input_frame, text="*", foreground="red").pack(side="left")

            if element['enum_options']:
                input_widget = ttk.Combobox(input_frame, textvariable=var, values=element['enum_options'])
                input_widget.set(element['value'])
            else:
                input_widget = ttk.Entry(input_frame, textvariable=var)

            input_widget.pack(side="left", fill="x", expand=True)
            self.entries[element['id']] = var

            # Display comment below the field
            if element['comment']:
                comment_label = ttk.Label(input_frame, text=element['comment'], wraplength=400, justify="left")
                comment_label.pack(fill="x", pady=(5, 0))

        # Add duplicate and remove buttons for multiple elements
        if element['multiple']:
            btn_frame = ttk.Frame(frame_container)
            btn_frame.pack(fill="x", padx=(indent + 5, 0))
            ttk.Button(btn_frame, text="+ Add",
                      command=lambda e=element: self.duplicate_element(e, input_container)).pack(side="left")
            ttk.Button(btn_frame, text="- Remove",
                      command=lambda e=element: self.remove_element(e, parent_frame)).pack(side="left")

        # Recursively create children
        for child in element['children']:
            self.create_widget(child, input_container if has_children else parent_frame, depth+1)

    def duplicate_element(self, element, parent_frame):
        # Create deep copy of the element
        new_element = copy.deepcopy(element)
        new_element['id'] = str(uuid.uuid4())  # Unique identifier for the new element
        new_element['parent']['children'].append(new_element)

        # Add the new element to the GUI
        self.create_widget(new_element, parent_frame)

    def remove_element(self, element, parent_frame):
        # Remove the element from the parent's children
        parent_element = element['parent']
        parent_element['children'].remove(element)

        # Rebuild the GUI
        self.build_gui()

    def save_xml_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
        if not file_path:
            return

        # Rebuild XML content
        output = []
        for element in self.xml_structure:
            if element['type'] == 'comment':
                output.append(element['comment'])
            elif element['type'] == 'element':
                self.generate_xml_content([element], output)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write('\n'.join(output))

        messagebox.showinfo("Success", "File saved successfully!")

    def generate_xml_content(self, elements, output):
        for element in elements:
            value = self.entries[element['id']].get() if element['id'] in self.entries else element['value']
            line = f"{element['indent']}<{element['tag']}>{value}</{element['tag']}>"
            if element['comment']:
                line += f" <!-- {element['comment']} -->"
            output.append(line)
            if element['children']:
                output.append(f"{element['indent']}<{element['tag']}>")
                self.generate_xml_content(element['children'], output)
                output.append(f"{element['indent']}</{element['tag']}>")

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLGeneratorApp(root)
    root.mainloop()
