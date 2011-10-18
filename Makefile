MARKUPPREVIEW_DIR = $(dir $(CURDIR)/$(lastword $(MAKEFILE_LIST)))
GEDIT_PLUGIN_DIR = ~/.gnome2/gedit/plugins

install:
	@if [ ! -d $(GEDIT_PLUGIN_DIR) ]; then \
		mkdir -p $(GEDIT_PLUGIN_DIR);\
	fi
	@echo "installing markup_preview plugin";
	@cp -R $(MARKUPPREVIEW_DIR)/plugin/markup_preview* $(GEDIT_PLUGIN_DIR);
	@rm -rf $(GEDIT_PLUGIN_DIR)/markup_preview/*.py[co];

uninstall:
	@echo "uninstalling markup_preview plugin";
	@rm -rf $(GEDIT_PLUGIN_DIR)/markup_preview*;

symlink:
	@echo "symlinking markup_preview plugin";
	@rm -rf $(GEDIT_PLUGIN_DIR)/markup_preview*;
	@ln -s $(MARKUPPREVIEW_DIR)/plugin/markup_preview $(GEDIT_PLUGIN_DIR)/markup_preview;
	@ln -s $(MARKUPPREVIEW_DIR)/plugin/markup_preview.gedit-plugin $(GEDIT_PLUGIN_DIR)/markup_preview.gedit-plugin;
