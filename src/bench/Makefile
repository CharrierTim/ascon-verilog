# Makefile running all testbenches

SUBDIRS := add_layer/ \
           diffusion_layer/ \
		   substitution_layer/sbox substitution_layer/substitution_layer \
		   xor/xor_begin xor/xor_end \
		   permutation \
		   ascon

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS) clean

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	@for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done