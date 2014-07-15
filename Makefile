PYTHON_EXECUTABLE=dynq.py
FINAL_EXECUTABLE=dynq
BUILD_DIR=build

.PHONY: all clean

all: clean package

clean:
	@rm -rfv $(BUILD_DIR)
	@rm -rfv *.pyc

package: create_virtualenv
	@rm -f $(BUILD_DIR)/$(FINAL_EXECUTABLE)
	@sh -c '. $(BUILD_DIR)/_virtualenv/bin/activate; python packagepy.py $(PYTHON_EXECUTABLE) $(BUILD_DIR)/$(FINAL_EXECUTABLE)'
	@chmod a+x $(BUILD_DIR)/$(FINAL_EXECUTABLE)
	@echo Package created.

create_virtualenv:
	@command -v virtualenv >/dev/null 2>&1 || { echo >&2 "This build requires virtualenv to be installed.  Aborting."; exit 1; }
	@mkdir -p $(BUILD_DIR)
	@if [ -d $(BUILD_DIR)/_virtualenv ]; then \
		echo "Existing virtualenv found. Skipping virtualenv creation."; \
	else \
		virtualenv $(BUILD_DIR)/_virtualenv; \
		sh -c '. $(BUILD_DIR)/_virtualenv/bin/activate; pip install .'; \
	fi
