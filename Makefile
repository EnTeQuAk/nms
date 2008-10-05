#
# NMS Makefile
# ~~~~~~~~~~~~
#
# Shortcuts for various tasks.

clean: clean-files reindent

clean-files:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '*.log' -exec rm -f {} +

clean-glade:
	@(python clean_glade.py)

reindent:
	@(echo "running reindent.py")
	@(python scripts/reindent.py -r -B .)
	@(echo "reindent... finished")

shell:
	@(python run.py shell)

run:
	@(python run.py run)
