#!/usr/bin/env python3
"""
Quick Knowledge Entry Tool
A simple GUI for quickly capturing support knowledge.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from knowledge import KnowledgeDB
import json

class QuickEntryGUI:
    def __init__(self):
        self.db = KnowledgeDB()
        self.root = tk.Tk()
        self.root.title("Quick Knowledge Entry")
        self.root.geometry("800x600")
        
        # Load config
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"categories": ["general"], "shopify_products": [""]}
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(main_frame, text="📝 Quick Knowledge Entry", 
                 font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Issue Title
        ttk.Label(main_frame, text="Issue Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=60)
        self.title_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Problem
        ttk.Label(main_frame, text="Problem:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
        self.problem_text = scrolledtext.ScrolledText(main_frame, height=6, width=60)
        self.problem_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Solution
        ttk.Label(main_frame, text="Solution:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        self.solution_text = scrolledtext.ScrolledText(main_frame, height=8, width=60)
        self.solution_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Category and Product row
        details_frame = ttk.Frame(main_frame)
        details_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(details_frame, text="Category:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.category_combo = ttk.Combobox(details_frame, values=self.config["categories"], width=20)
        self.category_combo.set("general")
        self.category_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(details_frame, text="Product:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.product_combo = ttk.Combobox(details_frame, values=self.config["shopify_products"], width=20)
        self.product_combo.grid(row=0, column=3)
        
        # Code Examples
        ttk.Label(main_frame, text="Code Examples:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        self.code_text = scrolledtext.ScrolledText(main_frame, height=4, width=60, font=("Courier", 10))
        self.code_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Tags
        ttk.Label(main_frame, text="Tags:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.tags_entry = ttk.Entry(main_frame, width=60)
        self.tags_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, text="(comma-separated)", font=("Arial", 8)).grid(row=7, column=1, sticky=tk.W)
        
        # Notes
        ttk.Label(main_frame, text="Notes:").grid(row=8, column=0, sticky=(tk.W, tk.N), pady=5)
        self.notes_text = scrolledtext.ScrolledText(main_frame, height=3, width=60)
        self.notes_text.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💾 Save Knowledge", 
                  command=self.save_knowledge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔍 Search Existing", 
                  command=self.search_knowledge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Clear Form", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", 
                  command=self.root.quit).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Focus on title field
        self.title_entry.focus()
    
    def save_knowledge(self):
        # Validate inputs
        title = self.title_entry.get().strip()
        problem = self.problem_text.get(1.0, tk.END).strip()
        solution = self.solution_text.get(1.0, tk.END).strip()
        
        if not title or not problem or not solution:
            messagebox.showerror("Error", "Please fill in Title, Problem, and Solution fields.")
            return
        
        # Get optional fields
        category = self.category_combo.get() or "general"
        product = self.product_combo.get() or None
        code = self.code_text.get(1.0, tk.END).strip() or None
        tags_str = self.tags_entry.get().strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else None
        notes = self.notes_text.get(1.0, tk.END).strip() or None
        
        try:
            # Save to database
            knowledge_uuid = self.db.add_knowledge(
                title=title,
                problem=problem,
                solution=solution,
                category=category,
                shopify_product=product,
                code_examples=code,
                tags=tags,
                notes=notes,
                source="gui"
            )
            
            messagebox.showinfo("Success", f"Knowledge saved successfully!\nUUID: {knowledge_uuid}")
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save knowledge: {str(e)}")
    
    def search_knowledge(self):
        # Simple search dialog
        search_term = tk.simpledialog.askstring("Search", "Enter search term:")
        if search_term:
            results = self.db.search_knowledge(query=search_term, limit=5)
            if results:
                result_text = "\n\n".join([
                    f"📝 {r['title']}\n💡 {r['solution'][:100]}..."
                    for r in results
                ])
                messagebox.showinfo("Search Results", result_text)
            else:
                messagebox.showinfo("Search Results", "No matching knowledge found.")
    
    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.problem_text.delete(1.0, tk.END)
        self.solution_text.delete(1.0, tk.END)
        self.code_text.delete(1.0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.notes_text.delete(1.0, tk.END)
        self.category_combo.set("general")
        self.product_combo.set("")
        self.title_entry.focus()
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    import tkinter.simpledialog
    app = QuickEntryGUI()
    app.run()


