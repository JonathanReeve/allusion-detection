essay.pdf : essay.md
	pandoc -o $@ $< \
		--smart \
		--latex-engine=xelatex \
		-V links-as-notes \
		--filter pandoc-crossref \
		--filter pandoc-citeproc
	evince '$@' &

mla: 
	pandoc -o essay.pdf essay.md \
		--smart \
		--latex-engine=xelatex \
		--template=mla-template.tex \
		--filter pandoc-crossref \
		--filter pandoc-citeproc
	gvfs-open essay.pdf &

docx: 
	pandoc -o essay.docx essay.md \
		--filter pandoc-crossref \
		--filter pandoc-citeproc \
		--smart \
		-V links-as-notes \
		--reference-docx=rmwm-reference.docx
	gvfs-open essay.docx &

odt: 
	pandoc -o essay.odt essay.md \
		--filter pandoc-crossref \
		--filter pandoc-citeproc \
		--smart \
		-V links-as-notes
	gvfs-open essay.odt &
