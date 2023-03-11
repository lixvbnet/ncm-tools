os = $(shell uname | awk '{print tolower($$0)}')
BIN_DIR = ~/bin

.PHONY: install create_folders install_py_files install_bin_files demo

install: create_folders install_py_files install_bin_files


install_py_files:
	@echo "Installing python files..."
	chmod +x *.py
	cp *.py $(BIN_DIR)

install_bin_files:
	@echo "Installing bin files..."
	cd bin/${os} && \
	chmod +x * && \
	cp * $(BIN_DIR)

create_folders:
	mkdir -p $(BIN_DIR)


# create demo gif
demo:
	cd docs/demo && \
	vhs < demo.tape
