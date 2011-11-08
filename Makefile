GEDIT_PLUGIN_DIR = ~/.local/share/gedit/plugins

install:
	@if [ ! -d $(GEDIT_PLUGIN_DIR) ]; then \
		mkdir -p $(GEDIT_PLUGIN_DIR);\
	fi
	@echo "installing markup_preview plugin";
	@rm -rf $(GEDIT_PLUGIN_DIR)/markup_preview*;
	@cp -R markup_preview* $(GEDIT_PLUGIN_DIR);

uninstall:
	@echo "uninstalling markup_preview plugin";
	@rm -rf $(GEDIT_PLUGIN_DIR)/markup_preview*;
