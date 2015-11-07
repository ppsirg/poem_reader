#!/usr/bin/env python3

"""
Copyright 2015 Stefano Benvenuti <ste.benve86@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import os
import json
import re
import lzma
import logging
from gi.repository import Gtk, Gio, Pango

# log options
log_level = logging.INFO
log_filename = "log/poem_reader.log"
log_format = "%(asctime)s - %(funcName)s : line %(lineno)d - %(levelname)s - %(message)s"
logging.basicConfig(filename=log_filename, format=log_format, level=log_level)

# helper function for reading a file content
def read_file(filename, is_json=False):

		logging.info("Opening \"%s\"", filename)
		f = None
		try:
			if is_json:
				logging.info("File \"%s\" is opened as a configuration json file", filename)
				f = open(filename)
				content = json.load(f)
			else:
				logging.info("File \"%s\" is opened as a compressed text file", filename)
				f = lzma.open(filename,'rt')
				content = f.read()
		except Exception as e:
			logging.error("File \"%s\" cannot be opened or read: %s", filename, e)
			sys.exit(1)
		finally:
			if f is not None:
				f.close()
		return content



class Poem_Chooser(Gtk.Window):


	def __init__(self):

		logging.info("Initializing Poem Chooser Dialog")
		Gtk.Window.__init__(self, title="Poem Chooser")
		# set main window border size
		self.set_border_width(20)
		# set main window minimum size
		self.set_size_request(600,400)

		# create the box
		dialog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10) 
		self.add(dialog_box)

		# create the ListStore model
		poems_liststore = Gtk.ListStore(str, str, str, str)
		# read the json file
		logging.info("Loading poems.json configuration file")
		self.data = read_file(os.path.join("poems", "poems.json"), is_json=True)
		# fill the ListStore
		languages_set = set()
		for poem, info in self.data.items():
			if "translator" in info:	
				translator = info["translator"]
			else:
				translator = "-"
			try:
				poems_liststore.append([poem, info["author"], info["language"], translator])
				logging.debug("Appended to the list store: %s, %s, %s, %s", poem, info["author"], info["language"], translator)
			except KeyError as e:
				logging.error("Missing key %s for poem \"%s\"", e, poem)
				sys.exit(1)
			# save the languages listed in the combobox
			languages_set.add(info["language"])
		
		# create the filter
		self.current_filter_language = "All"
		self.language_filter = poems_liststore.filter_new()
		self.language_filter.set_visible_func(self.language_filter_func)

		# create the treeview
		self.treeview = Gtk.TreeView.new_with_model(Gtk.TreeModelSort(self.language_filter))
		for index, column_title in enumerate(["Title", "Author", "Language", "Translator(s)"]):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=index)
			column.set_sort_column_id(0)
			self.treeview.append_column(column)
		self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

		# create combobox to filter by language
		languages_list = sorted(languages_set)
		languages_list.insert(0, "All")
		language_combo = Gtk.ComboBoxText.new()
		for language in languages_list:
			language_combo.insert(-1, None, language)
			logging.debug("Inserted language: %s", language)
		language_combo.connect("changed", self.on_language_combo_changed)
		language_combo.set_entry_text_column(0)
		language_combo.set_active(0)
		dialog_box.pack_start(language_combo, False, False, 0)

		# create a scrolled window
		scrollable_treelist = Gtk.ScrolledWindow()
		scrollable_treelist.add(self.treeview)
		dialog_box.pack_start(scrollable_treelist, True, True, 0)

		# create open button
		button = Gtk.Button("Open")
		button.connect("clicked", self.on_open_button_clicked)
		dialog_box.pack_start(button, False, False, 0)


	def language_filter_func(self, model, iterator, data):

		# tests if the language in the row is the one in the filter
		if self.current_filter_language == "All":
			return True
		else:
			return model[iterator][2] == self.current_filter_language


	def on_language_combo_changed(self, combo):

		# set the current language filter to the button label
		self.current_filter_language = combo.get_active_text()
		# update the filter
		self.language_filter.refilter()


	def on_open_button_clicked(self, button):

		# get selected row
		(model, rows) = self.treeview.get_selection().get_selected_rows()
		if len(rows) > 0:
			tree_iter = model.get_iter(rows[0])
			poem = model.get_value(tree_iter, 0)
			logging.info("Opening poem: %s", poem)
			# close dialog window
			self.destroy()
			logging.info("Poem Chooser Dialog destroyed")
			# open main application window
			win = Divine_Comedy_Reader(poem, self.data)
			win.connect("delete-event", Gtk.main_quit)
			win.show_all()



class Divine_Comedy_Reader(Gtk.Window):


	def __init__(self, poem, data):

		logging.info("Initializing Poem Reader Window")
		Gtk.Window.__init__(self)
		# current poem
		self.poem = poem
		# data read from the json file
		try:
			self.root = data[self.poem]
			self.folder = data[self.poem]["folder"]
			self.chapters = data[self.poem]["chapters"]
			self.separator = data[self.poem]["separator"]
		except KeyError as e:
			logging.error("Missing key %s", e)
			sys.exit(1)
		# set main window border size
		self.set_border_width(20)
		# set main window minimum size
		self.set_size_request(700,700)
		# create header
		self.create_header()
		# create body
		self.create_body()


	def create_header(self):

		# add header bar
		header_bar = Gtk.HeaderBar()
		header_bar.set_show_close_button(True)
		self.set_titlebar(header_bar)

		# add choose poem button to header bar
		button = Gtk.Button()
		icon = Gio.ThemedIcon(name="content-loading-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.set_tooltip_text("Choose poem")
		button.connect("clicked", self.on_choose_poem_clicked)
		header_bar.pack_start(button)

		# add go to bookmark button to header bar
		button = Gtk.Button()
		icon = Gio.ThemedIcon(name="go-jump-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.set_tooltip_text("Go to bookmark")
		button.connect("clicked", self.on_go_to_bookmark_clicked)
		header_bar.pack_end(button)

		# add new bookmark button to header bar
		button = Gtk.Button()
		icon = Gio.ThemedIcon(name="bookmark-add-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.set_tooltip_text("Set bookmark")
		button.connect("clicked", self.on_add_bookmark_clicked)
		header_bar.pack_end(button)

		# add stack switcher to header bar
		self.stack = Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		self.stack.set_transition_duration(1000)
		self.textviews = {}
		for chapter in self.chapters:
			logging.debug("Adding chapter \"%s\" to header bar", chapter)
			# create a scrolled window which contains a text view
			scrolledwindow = Gtk.ScrolledWindow()
			# create a text view
			textview = Gtk.TextView()
			textview.set_justification(Gtk.Justification.CENTER)
			textview.set_wrap_mode(Gtk.WrapMode.WORD)
			textview.set_editable(False)
			textview.set_cursor_visible(False)
			textbuffer = textview.get_buffer()
			textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
			textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
			scrolledwindow.add(textview)
			# add scrolled window to stack
			self.stack.add_titled(scrolledwindow, chapter, chapter)
			# for each chapter an array with the textview, the current canto and the scrolled window
			self.textviews[chapter] = [textview, 0, scrolledwindow]
		stack_switcher = Gtk.StackSwitcher()
		stack_switcher.set_stack(self.stack)
		header_bar.set_custom_title(stack_switcher)


	def create_body(self):

		# create box for text window
		main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.add(main_box)

		# add poem title
		label = Gtk.Label(self.poem)
		label.set_markup("<span size=\"x-large\">" + self.poem + "</span>")
		main_box.pack_start(label, False, False, 0)

		# add navigation buttons to the box
		navigation_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		Gtk.StyleContext.add_class(navigation_box.get_style_context(), "linked")
		button = Gtk.Button()
		button.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
		button.set_size_request(30,30)
		button.set_tooltip_text("Previous Canto")
		button.connect("clicked", self.on_nav_clicked, -1)
		navigation_box.pack_start(button, True, True, 0)
		button = Gtk.Button()
		button.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
		button.set_size_request(30,30)
		button.set_tooltip_text("Next Canto")
		button.connect("clicked", self.on_nav_clicked, 1)
		navigation_box.pack_start(button, True, True, 0)
		main_box.pack_start(navigation_box, False, False, 0)

		# read the text files
		self.cantos = {}
		for chapter in self.chapters:
			logging.debug("Adding content for chapter \"%s\"", chapter)
			chapter_file  = self.root[chapter]
			# open the text file containing the chapter
			content = read_file(os.path.join("poems", self.folder, chapter_file))
			# divide the chapter in cantos using canto_name as separator
			self.cantos[chapter] = [self.separator + c for c in content.split(self.separator)[1:]]
			textbuffer = self.textviews[chapter][0].get_buffer()
			textbuffer.set_text(self.cantos[chapter][0])
			self.apply_tags(textbuffer)
		# add stack (see create_header) to the container
		main_box.pack_start(self.stack, True, True, 30)


	def on_choose_poem_clicked(self, button):

		# close current window
		self.destroy()
		logging.info("Poem Reader Window destroyed")
		# open dialog window
		win = Poem_Chooser()
		win.connect("delete-event", Gtk.main_quit)
		win.show_all()


	def on_nav_clicked(self, button, step):

		# previous canto if step is -1, next canto if step is 1 
		current_chapter = self.stack.get_visible_child_name()
		current_canto = self.textviews[current_chapter][1]
		if (step < 0 and current_canto > 0) or (step > 0 and current_canto < (len(self.cantos[current_chapter]) - 1)):
			logging.debug("Nav clicked with step %d", step)
			current_canto += step
			# update text buffer	
			textbuffer = self.textviews[current_chapter][0].get_buffer()
			textbuffer.set_text(self.cantos[current_chapter][current_canto])
			self.apply_tags(textbuffer)
			# update current canto in self.textviews
			self.textviews[current_chapter][1] = current_canto


	def on_add_bookmark_clicked(self, button):

		# save current status to a file
		current_chapter = self.stack.get_visible_child_name()
		logging.info("Adding bookmark file for chapter \"%s\" of poem \"%s\"", current_chapter, self.poem)
		f = None
		try:
			f = open(os.path.join("poems",self.folder,"bookmark.txt"),'w')
			f.write(current_chapter + " " + str(self.textviews[current_chapter][1]) + "\n")
		except Exception as e:
			logging.error("Bookmark file for poem \"%s\" cannot be opened or written: %s", self.poem, e)
			sys.exit(1)
		finally:
			if f is not None:
				f.close()


	def on_go_to_bookmark_clicked(self, button):

		# go to saved chapter and canto
		if os.path.isfile(os.path.join("poems",self.folder,"bookmark.txt")):
			logging.info("Going to bookmark for poem \"%s\"", self.poem)
			f = None
			try:
				f = open(os.path.join("poems",self.folder,"bookmark.txt"))
				(chapter, canto) = f.readline().strip().split(" ")
			except Exception as e:
				logging.error("Bookmark file for poem \"%s\" cannot be opened or read: %s", self.poem, e)
				sys.exit(1)
			finally:
				if f is not None:
					f.close()
			try:
				# set visible scrolled window
				self.stack.set_visible_child(self.textviews[chapter][2])
				# set current canto
				self.textviews[chapter][1] = int(canto)
				# set textbuffer in the textview
				textbuffer = self.textviews[chapter][0].get_buffer()
				textbuffer.set_text(self.cantos[chapter][int(canto)])
			except KeyError as e:
				logging.error("Missing key %s", e)
				sys.exit(1)
			self.apply_tags(textbuffer) 


	def apply_tags(self, textbuffer):

		# change font style
		logging.debug("Applying tags")
		textiter_start = textbuffer.get_start_iter()
		textiter_end = textbuffer.get_start_iter()
		while not textiter_start.is_end():
			textiter_end.forward_to_line_end()
			current_text = textiter_start.get_text(textiter_end)
			if re.search("(\(\d+\)|\[.*])", current_text):
				logging.debug("Applying italic for text \"%s\"", current_text)
				textbuffer.apply_tag_by_name("italic", textiter_start, textiter_end)	
			elif re.search(self.separator, current_text):
				logging.debug("Applying bold for text \"%s\"", current_text)
				textbuffer.apply_tag_by_name("bold", textiter_start, textiter_end) 
			textiter_start.forward_line()




win = Poem_Chooser()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
