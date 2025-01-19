# Makefile can be in ./subdir/Makefile or ./subdir/another/Makefile
SUBDIRS := $(shell find . -mindepth 1 -maxdepth 1 -type d) 

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS) clean

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	@for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done