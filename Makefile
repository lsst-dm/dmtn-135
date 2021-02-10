DOCTYPE = DMTN
DOCNUMBER = 135
DOCNAME = $(DOCTYPE)-$(DOCNUMBER)

tex = $(filter-out $(wildcard *acronyms.tex) , $(wildcard *.tex))

GITVERSION := $(shell git log -1 --date=short --pretty=%h)
GITDATE := $(shell git log -1 --date=short --pretty=%ad)
GITSTATUS := $(shell git status --porcelain)
ifneq "$(GITSTATUS)" ""
	GITDIRTY = -dirty
endif

export TEXMFHOME ?= lsst-texmf/texmf

# Add aglossary.tex as a dependancy here if you want a glossary
$(DOCNAME).pdf: $(tex) meta.tex local.bib
	latexmk -bibtex -xelatex -f $(DOCNAME)
#	makeglossaries $(DOCNAME)      
#	xelatex $(SRC)
# For glossary uncomment the 2 lines abouve


# Acronym tool allows for selection of acronyms based on tags - you may want more than DM
acronyms.tex: $(tex) myacronyms.txt
	$(TEXMFHOME)/../bin/generateAcronyms.py -t "DM" $(tex)

# If you want a glossary you must manually run generateAcronyms.py  -gu to put the \gls in your files.
aglossary.tex :$(tex) myacronyms.txt
	generateAcronyms.py  -g $(tex)

gdepend:
	pip install --upgrade google-api-python-client google-auth-httplib2  google-auth-oauthlib  oauth2client
tables:
	makeTablesFromGoogle.py 1DiFTjsC4dP8XyOV7-uF0zwkl0r0jMuW9U9uELejpmn8 Model\!A1:H Storage\!A1:H Compute\!A1:H "Ops Storage"\!A1:L "Ops Compute"\!A1:L "Ops Costs"\!A1:L "Cloud"\!A1:M9 "PreOps"\!A1:E

.PHONY: clean
clean:
	latexmk -c
	rm -f $(DOCNAME).bbl
	rm -f $(DOCNAME).pdf
	rm -f meta.tex

.FORCE:

meta.tex: Makefile .FORCE
	rm -f $@
	touch $@
	echo '% GENERATED FILE -- edit this in the Makefile' >>$@
	/bin/echo '\newcommand{\lsstDocType}{$(DOCTYPE)}' >>$@
	/bin/echo '\newcommand{\lsstDocNum}{$(DOCNUMBER)}' >>$@
	/bin/echo '\newcommand{\vcsRevision}{$(GITVERSION)$(GITDIRTY)}' >>$@
	/bin/echo '\newcommand{\vcsDate}{$(GITDATE)}' >>$@
