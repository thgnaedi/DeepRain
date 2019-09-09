# Files and folders
SRC   :=Langdokumentation.tex
SUBSRC:=*.tex
IMGDIR:=pics

# Programs and arguments
LATEXMK    :=latexmk
LATEXMKARGS:=-pdf

# Targets, used for creating single recipes and autocompletion
TARGET:=$(SRC:.tex=.pdf)


# Implicit pdf rule for PDFs
%.pdf: %.tex
	$(LATEXMK) $(LATEXMKARGS) $<

$(TARGET): $(SRC) $(SUBSRC) $(IMGDIR)/*


.PHONY: clean cleanup war love

# Clean all temporary files, keep target PDFs
clean:
	latexmk -c
	rm -f *.aux *.bbl *.fdb_latexmk *.fls *.glg *.glo *.gls *.idx *.ilg *.ind *.ist *.log *.lol *.out *.synctex.gz

# Clean all created files
cleanup: clean
	latexmk -C
	rm -f *.pdf

war:
	@echo "Not love?"

love:
	@echo "Not war?"
