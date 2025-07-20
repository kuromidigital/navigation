import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from pathlib import Path


class NavManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("导航数据管理工具")
        self.root.geometry("1000x600")

        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TTreeview", font=("SimHei", 10))

        # 数据存储
        self.data = []
        self.current_file = None

        # 创建界面
        self.create_widgets()

        # 尝试加载默认文件
        self.load_default_file()

    def create_widgets(self):
        # 顶部菜单
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="新建", command=self.new_file)
        filemenu.add_command(label="打开", command=self.open_file)
        filemenu.add_command(label="保存", command=self.save_file)
        filemenu.add_command(label="另存为", command=self.save_file_as)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        self.root.config(menu=menubar)

        # 主界面分为左右两部分
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧：分类和链接列表
        left_frame = ttk.LabelFrame(main_frame, text="导航列表")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 分类列表
        category_frame = ttk.Frame(left_frame)
        category_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(category_frame, text="分类:").pack(side=tk.LEFT, padx=5)
        self.category_listbox = tk.Listbox(category_frame, width=30, height=10)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        category_btn_frame = ttk.Frame(category_frame)
        category_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        ttk.Button(category_btn_frame, text="添加分类", command=self.add_category).pack(fill=tk.X, pady=2)
        ttk.Button(category_btn_frame, text="编辑分类", command=self.edit_category).pack(fill=tk.X, pady=2)
        ttk.Button(category_btn_frame, text="删除分类", command=self.delete_category).pack(fill=tk.X, pady=2)

        # 链接列表
        link_frame = ttk.LabelFrame(left_frame, text="链接")
        link_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("name", "url")
        self.link_tree = ttk.Treeview(link_frame, columns=columns, show="headings")
        self.link_tree.heading("name", text="名称")
        self.link_tree.heading("url", text="URL")
        self.link_tree.column("name", width=100)
        self.link_tree.column("url", width=300)
        self.link_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.link_tree.bind('<<TreeviewSelect>>', self.on_link_select)

        link_btn_frame = ttk.Frame(link_frame)
        link_btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(link_btn_frame, text="添加链接", command=self.add_link).pack(side=tk.LEFT, padx=5)
        ttk.Button(link_btn_frame, text="编辑链接", command=self.edit_link).pack(side=tk.LEFT, padx=5)
        ttk.Button(link_btn_frame, text="删除链接", command=self.delete_link).pack(side=tk.LEFT, padx=5)

        # 右侧：预览区域
        right_frame = ttk.LabelFrame(main_frame, text="预览")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_text = tk.Text(right_frame, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text.config(state=tk.DISABLED)

        # 底部状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_default_file(self):
        """尝试加载当前目录下的navData.json文件"""
        default_path = Path("navData.json")
        if default_path.exists():
            self.current_file = str(default_path)
            self.load_file(self.current_file)

    def load_file(self, file_path):
        """从文件加载导航数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.update_ui()
            self.status_var.set(f"已加载: {os.path.basename(file_path)}")
            self.update_preview()
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")

    def save_file(self):
        """保存当前文件"""
        if not self.current_file:
            return self.save_file_as()

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"已保存: {os.path.basename(self.current_file)}")
            self.update_preview()
            messagebox.showinfo("成功", "文件已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")

    def save_file_as(self):
        """另存为新文件"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            self.current_file = file_path
            self.save_file()

    def new_file(self):
        """创建新文件"""
        if messagebox.askyesno("确认", "是否创建新文件？当前更改将丢失。"):
            self.data = []
            self.current_file = None
            self.update_ui()
            self.update_preview()
            self.status_var.set("新建文件")

    def open_file(self):
        """打开文件对话框"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            self.current_file = file_path
            self.load_file(file_path)

    def update_ui(self):
        """更新界面显示"""
        # 清空分类列表
        self.category_listbox.delete(0, tk.END)

        # 填充分类列表
        for category in self.data:
            self.category_listbox.insert(tk.END, category["title"])

        # 清空链接列表
        for item in self.link_tree.get_children():
            self.link_tree.delete(item)

    def on_category_select(self, event):
        """分类选择事件处理"""
        selection = self.category_listbox.curselection()
        if not selection:
            return

        category_index = selection[0]
        category = self.data[category_index]

        # 清空链接列表
        for item in self.link_tree.get_children():
            self.link_tree.delete(item)

        # 填充链接列表
        for link in category["links"]:
            self.link_tree.insert("", tk.END, values=(link["name"], link["url"]))

    def on_link_select(self, event):
        """链接选择事件处理"""
        pass

    def add_category(self):
        """添加分类"""
        category_name = simpledialog.askstring("添加分类", "请输入分类名称:")
        if category_name and category_name.strip():
            category_name = category_name.strip()
            self.data.append({"title": category_name, "links": []})
            self.update_ui()
            self.save_file()

    def edit_category(self):
        """编辑分类"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个分类")
            return

        category_index = selection[0]
        old_name = self.data[category_index]["title"]

        new_name = simpledialog.askstring("编辑分类", "请输入新的分类名称:", initialvalue=old_name)
        if new_name and new_name.strip() and new_name != old_name:
            self.data[category_index]["title"] = new_name.strip()
            self.update_ui()
            self.save_file()

    def delete_category(self):
        """删除分类"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个分类")
            return

        category_index = selection[0]
        category_name = self.data[category_index]["title"]

        if messagebox.askyesno("确认删除", f"确定要删除分类 '{category_name}' 及其所有链接吗？"):
            del self.data[category_index]
            self.update_ui()
            self.save_file()

    def add_link(self):
        """添加链接"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个分类")
            return

        category_index = selection[0]

        # 创建添加链接对话框
        link_dialog = tk.Toplevel(self.root)
        link_dialog.title("添加链接")
        link_dialog.geometry("400x200")
        link_dialog.transient(self.root)
        link_dialog.grab_set()

        ttk.Label(link_dialog, text="名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(link_dialog, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(link_dialog, text="URL:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        url_entry = ttk.Entry(link_dialog, width=40)
        url_entry.grid(row=1, column=1, padx=10, pady=10)

        def save_link():
            name = name_entry.get().strip()
            url = url_entry.get().strip()

            if not name or not url:
                messagebox.showinfo("提示", "名称和URL不能为空")
                return

            self.data[category_index]["links"].append({"name": name, "url": url})
            self.on_category_select(None)  # 刷新链接列表
            self.save_file()
            link_dialog.destroy()

        ttk.Button(link_dialog, text="保存", command=save_link).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(link_dialog, text="取消", command=link_dialog.destroy).grid(row=2, column=1, padx=10, pady=20)

        link_dialog.mainloop()

    def edit_link(self):
        """编辑链接"""
        category_selection = self.category_listbox.curselection()
        if not category_selection:
            messagebox.showinfo("提示", "请先选择一个分类")
            return

        link_selection = self.link_tree.selection()
        if not link_selection:
            messagebox.showinfo("提示", "请先选择一个链接")
            return

        category_index = category_selection[0]
        link_item = self.link_tree.item(link_selection[0])
        old_name, old_url = link_item["values"]

        # 创建编辑链接对话框
        link_dialog = tk.Toplevel(self.root)
        link_dialog.title("编辑链接")
        link_dialog.geometry("400x200")
        link_dialog.transient(self.root)
        link_dialog.grab_set()

        ttk.Label(link_dialog, text="名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(link_dialog, width=40)
        name_entry.insert(0, old_name)
        name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(link_dialog, text="URL:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        url_entry = ttk.Entry(link_dialog, width=40)
        url_entry.insert(0, old_url)
        url_entry.grid(row=1, column=1, padx=10, pady=10)

        link_index = self.link_tree.index(link_selection[0])

        def save_link():
            name = name_entry.get().strip()
            url = url_entry.get().strip()

            if not name or not url:
                messagebox.showinfo("提示", "名称和URL不能为空")
                return

            self.data[category_index]["links"][link_index] = {"name": name, "url": url}
            self.on_category_select(None)  # 刷新链接列表
            self.save_file()
            link_dialog.destroy()

        ttk.Button(link_dialog, text="保存", command=save_link).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(link_dialog, text="取消", command=link_dialog.destroy).grid(row=2, column=1, padx=10, pady=20)

        link_dialog.mainloop()

    def delete_link(self):
        """删除链接"""
        category_selection = self.category_listbox.curselection()
        if not category_selection:
            messagebox.showinfo("提示", "请先选择一个分类")
            return

        link_selection = self.link_tree.selection()
        if not link_selection:
            messagebox.showinfo("提示", "请先选择一个链接")
            return

        category_index = category_selection[0]
        link_item = self.link_tree.item(link_selection[0])
        link_name = link_item["values"][0]

        if messagebox.askyesno("确认删除", f"确定要删除链接 '{link_name}' 吗？"):
            link_index = self.link_tree.index(link_selection[0])
            del self.data[category_index]["links"][link_index]
            self.on_category_select(None)  # 刷新链接列表
            self.save_file()

    def update_preview(self):
        """更新预览区域"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        if not self.data:
            self.preview_text.insert(tk.END, "导航数据为空")
        else:
            for category in self.data:
                self.preview_text.insert(tk.END, f"【{category['title']}】\n", "category")
                for link in category["links"]:
                    self.preview_text.insert(tk.END, f"  {link['name']}: {link['url']}\n", "link")
                self.preview_text.insert(tk.END, "\n")

        # 设置文本样式
        self.preview_text.tag_config("category", font=("SimHei", 12, "bold"))
        self.preview_text.tag_config("link", font=("SimHei", 10))

        self.preview_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = NavManagerApp(root)
    root.mainloop()