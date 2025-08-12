make: ppparis pref01 pref02 pref03 pref04 pref05 pref06 pref09 pref10 pref11 pref13 pref2a pref2b pref23 pref25 pref29 pref30 pref31 pref33 pref34 pref35 pref38 pref39 pref42 pref44 pref49 pref50 pref52 pref54 pref55 pref59 pref61 pref62 pref63 pref64 pref65 pref66 pref69 pref73 pref74 pref75 pref76 pref77 pref80 pref81 pref83 pref87 pref91 pref92 pref93 pref94 pref976 prefbretagne prefidf prefpaca
ppparis:
	bin/python3 cli.py ppparis
pref01:
	bin/python3 cli.py pref01
pref02:
	bin/python3 cli.py pref02
pref03:
	bin/python3 cli.py pref03
pref04:
	bin/python3 cli.py pref04
pref05:
	bin/python3 cli.py pref05
pref06:
	bin/python3 cli.py pref06
pref09:
	bin/python3 cli.py pref09
pref10:
	bin/python3 cli.py pref10
pref11:
	bin/python3 cli.py pref11
pref13:
	bin/python3 cli.py pref13
pref2a:
	bin/python3 cli.py pref2a
pref2b:
	bin/python3 cli.py pref2b
pref23:
	bin/python3 cli.py pref23
pref25:
	bin/python3 cli.py pref25
pref29:
	bin/python3 cli.py pref29
pref30:
	bin/python3 cli.py pref30
pref31:
	bin/python3 cli.py pref31
pref33:
	bin/python3 cli.py pref33
pref34:
	bin/python3 cli.py pref34
pref35:
	bin/python3 cli.py pref35
pref38:
	bin/python3 cli.py pref38
pref39:
	bin/python3 cli.py pref39
pref42:
	bin/python3 cli.py pref42
pref44:
	bin/python3 cli.py pref44
pref49:
	bin/python3 cli.py pref49
pref50:
	bin/python3 cli.py pref50
pref52:
	bin/python3 cli.py pref52
pref54:
	bin/python3 cli.py pref54
pref55:
	bin/python3 cli.py pref55
pref59:
	bin/python3 cli.py pref59
pref61:
	bin/python3 cli.py pref61
pref62:
	bin/python3 cli.py pref62
pref63:
	bin/python3 cli.py pref63
pref64:
	bin/python3 cli.py pref64
pref65:
	bin/python3 cli.py pref65
pref66:
	bin/python3 cli.py pref66
pref69:
	bin/python3 cli.py pref69
pref73:
	bin/python3 cli.py pref73
pref74:
	bin/python3 cli.py pref74
pref75:
	bin/python3 cli.py pref75
pref76:
	bin/python3 cli.py pref76
pref77:
	bin/python3 cli.py pref77
pref80:
	bin/python3 cli.py pref80
pref81:
	bin/python3 cli.py pref81
pref83:
	bin/python3 cli.py pref83
pref87:
	bin/python3 cli.py pref87
pref91:
	bin/python3 cli.py pref91
pref92:
	bin/python3 cli.py pref92
pref93:
	bin/python3 cli.py pref93
pref94:
	bin/python3 cli.py pref94
pref976:
	bin/python3 cli.py pref976
prefbretagne:
	bin/python3 cli.py prefbretagne
prefidf:
	bin/python3 cli.py prefidf
prefpaca:
	bin/python3 cli.py prefpaca
lint:
	bin/pycodestyle --first --show-source --ignore=E402,E501 *.py misc/*.py
