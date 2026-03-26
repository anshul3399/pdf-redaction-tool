"""
PDF Coordinate Picker

A graphical tool to visually select and obtain coordinates of areas to redact from a PDF.

Usage:
    python find_coordinates.py

Instructions:
    1. Select a PDF file from the file browser
    2. The first page will display at 2x zoom for precision
    3. Click and drag to select the area you want to redact
    4. Coordinates will appear in the console and on screen
    5. Copy the coordinates and use them in apply_redaction_at_coordinates_globally.py

Author: PDF Redaction Tool
License: MIT
"""

import fitz
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys


class PDFCoordinatePicker:
    """
    Interactive GUI for selecting and obtaining PDF coordinates.
    
    Displays the first page of a PDF at 2x zoom and allows user to
    click and drag to select a rectangular redaction area.
    """
    
    ZOOM_FACTOR = 1.0  # default display zoom (can be changed interactively)
    ZOOM_STEP = 0.25
    MIN_ZOOM = 0.25
    MAX_ZOOM = 4.0
    
    def __init__(self):
        """Initialize the coordinate picker application."""
        self.root = tk.Tk()
        self.root.title("PDF Coordinate Picker - Find Areas to Redact")
        
        # File selection dialog
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            messagebox.showinfo("Cancelled", "No file selected. Exiting.")
            self.root.destroy()
            return
        
        try:
            # Open PDF
            self.pdf = fitz.open(file_path)
            self.total_pages = len(self.pdf)
            self.current_page = 0
            self.page = self.pdf[self.current_page]
            print(f"✓ Loaded PDF: {file_path}")
            print(f"  Total pages: {self.total_pages}")
            print()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF:\n{str(e)}")
            self.root.destroy()
            return
        
        self.zoom = self.ZOOM_FACTOR
        
        try:
            pix = self.page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to render PDF:\n{str(e)}")
            self.root.destroy()
            return
        
        # Create scrollable canvas for displaying PDF
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, width=pix.width, height=pix.height, cursor="crosshair")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.vbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        # Store image reference to prevent garbage collection
        self.photo = ImageTk.PhotoImage(img)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))

        # Set initial window size
        self.root.geometry(f"{min(pix.width+20, 1000)}x{min(pix.height+160, 800)}")
        
        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.prev_button = tk.Button(nav_frame, text="Previous Page", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.goto_label = tk.Label(nav_frame, text="Go to page:")
        self.goto_label.pack(side=tk.LEFT, padx=(10, 2))

        self.goto_entry = tk.Entry(nav_frame, width=4)
        self.goto_entry.pack(side=tk.LEFT, padx=(0, 2))
        self.goto_entry.bind("<Return>", lambda event: self.go_to_page())
        self.goto_entry.focus_set()

        self.goto_button = tk.Button(nav_frame, text="Go", command=self.go_to_page)
        self.goto_button.pack(side=tk.LEFT, padx=(0, 10))

        self.page_label = tk.Label(nav_frame, text=f"Page {self.current_page + 1} of {self.total_pages}", font=("Arial", 10, "bold"))
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.zoom_out_button = tk.Button(nav_frame, text="Zoom -", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.zoom_in_button = tk.Button(nav_frame, text="Zoom +", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.next_button = tk.Button(nav_frame, text="Next Page", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Update button states
        self.update_nav_buttons()
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)

        # State variables
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        # Status label
        self.label = tk.Label(
            self.root,
            text="Click and drag to select redaction area",
            font=("Arial", 11),
            fg="green"
        )
        self.label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Selection storage (page, coords)
        self.selections = []

        # Print final output when window closes
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        
        # Instructions frame
        instructions = tk.Label(
            self.root,
            text="Navigation: Prev/Next pages, Zoom +/- or mouse wheel, click-drag area for coords",
            font=("Arial", 9),
            fg="gray"
        )
        instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        print("=" * 60)
        print("PDF COORDINATE PICKER")
        print("=" * 60)
        print("Instructions:")
        print("  • Use Previous/Next buttons to navigate pages")
        print("  • Use Zoom +/- buttons or mouse wheel to change zoom")
        print("  • Click and drag to select the area to redact")
        print("  • Coordinates will be printed below and in the window")
        print("  • Make multiple selections by dragging again")
        print("=" * 60)
        print()
        
        self.root.mainloop()
    
    def on_click(self, event):
        """Handle mouse click - start of selection."""
        # Convert from canvas coordinates to actual page coordinates (account for zoom)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.start_x = x / self.zoom
        self.start_y = y / self.zoom
    
    def on_drag(self, event):
        """Handle mouse drag - update selection rectangle."""
        # Remove previous rectangle
        if self.rect:
            self.canvas.delete(self.rect)
        
        # Draw rectangle at current zoom level (visual display)
        curr_x = self.canvas.canvasx(event.x)
        curr_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(
            self.start_x * self.zoom,
            self.start_y * self.zoom,
            curr_x,
            curr_y,
            outline="red",
            width=2
        )
    
    def on_release(self, event):
        """Handle mouse release - finalize selection."""
        # Convert from canvas coordinates to actual page coordinates (account for zoom)
        end_x = self.canvas.canvasx(event.x) / self.zoom
        end_y = self.canvas.canvasy(event.y) / self.zoom
        
        # Ensure coordinates are in correct order
        x0 = min(self.start_x, end_x)
        y0 = min(self.start_y, end_y)
        x1 = max(self.start_x, end_x)
        y1 = max(self.start_y, end_y)
        
        # Display coordinates
        coords_text = f"Coordinates: ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
        python_code = f"redact_area = fitz.Rect({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
        
        print(coords_text)
        print(f"Python code: {python_code}")
        print()
        
        # Save selection for later batch output
        self.selections.append({
            "page": self.current_page + 1,
            "coords": (x0, y0, x1, y1)
        })

        # Update label
        self.label.config(text=coords_text, fg="blue")
    
    def update_nav_buttons(self):
        """Update navigation button states."""
        self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)
    
    def display_page(self, page_num):
        """Display the specified page."""
        try:
            self.page = self.pdf[page_num]
            pix = self.page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Update window and canvas size
            self.root.geometry(f"{min(pix.width+20, 1000)}x{min(pix.height+160, 800)}")
            self.canvas.config(width=pix.width, height=pix.height)
            
            # Delete old image and create new one
            self.canvas.delete(self.image_item)
            self.photo = ImageTk.PhotoImage(img)
            self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
            self.root.title(f"PDF Coordinate Picker - Page {page_num + 1}/{self.total_pages} - Zoom {int(self.zoom*100)}%")
            
            # Clear any existing selection rectangle
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None
            
            # Update page label
            self.page_label.config(text=f"Page {page_num + 1} of {self.total_pages}")
            
            # Reset selection state
            self.start_x = None
            self.start_y = None
            
            # Update label
            self.label.config(text="Click and drag to select redaction area", fg="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page {page_num + 1}:\n{str(e)}")
    
    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)
            self.update_nav_buttons()
    
    def zoom_in(self):
        """Zoom in and refresh the page."""
        new_zoom = min(self.zoom + self.ZOOM_STEP, self.MAX_ZOOM)
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            self.display_page(self.current_page)

    def zoom_out(self):
        """Zoom out and refresh the page."""
        new_zoom = max(self.zoom - self.ZOOM_STEP, self.MIN_ZOOM)
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            self.display_page(self.current_page)

    def on_mousewheel(self, event):
        """Handle mouse wheel to zoom."""
        if hasattr(event, 'delta'):
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            if event.num == 4:
                self.zoom_in()
            elif event.num == 5:
                self.zoom_out()

    def go_to_page(self):
        """Go to the user-entered page number."""
        page_text = self.goto_entry.get().strip()
        if not page_text:
            messagebox.showwarning("Invalid page", "Please enter a page number")
            self.goto_entry.focus_set()
            return

        if not page_text.isdigit():
            messagebox.showwarning("Invalid page", "Enter a positive integer page number")
            self.goto_entry.focus_set()
            return

        page_num = int(page_text)
        if page_num < 1 or page_num > self.total_pages:
            messagebox.showwarning("Invalid page", f"Page must be between 1 and {self.total_pages}")
            self.goto_entry.focus_set()
            return

        self.current_page = page_num - 1
        self.display_page(self.current_page)
        self.update_nav_buttons()
        self.goto_entry.delete(0, tk.END)
        self.goto_entry.focus_set()

    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page(self.current_page)
            self.update_nav_buttons()

    def on_close(self):
        """On close, print a ready-to-use block for apply_redaction_at_coordinates_globally.py."""
        if self.selections:
            print("\n=== COPY-PASTE REDACTION_AREAS BLOCK FOR apply_redaction_at_coordinates_globally.py ===")
            print("REDACTION_AREAS = [")
            for sel in self.selections:
                coords = sel['coords']
                page = sel['page']
                print(f"    {{'coords': ({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}, {coords[3]:.1f}), 'pages': '{page}' }},")
            print("]")
            print("=== END OF BLOCK ===\n")

        self.root.destroy()


def main():
    """Main entry point."""
    try:
        picker = PDFCoordinatePicker()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()