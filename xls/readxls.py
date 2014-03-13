import os
from datetime import datetime
import xlrd
from xlrd.timemachine import REPR



def check(ts):
	BEGIN_TIME = time_to_int("09:00")
	MID1_TIME  = time_to_int("12:00")
	MID2_TIME  = time_to_int("14:00")
	END_TIME   = time_to_int("18:00")

	if len(ts) <= 0:
		return 0

	# import pdb; pdb.set_trace()
	b, e = ts[0], ts[-1]
	m1, m2 = MID1_TIME, MID2_TIME
	if b > e:
		b, e = e, b

	if b < BEGIN_TIME:
		if e < BEGIN_TIME:
			return 0
		elif e < MID1_TIME:
			return  e - BEGIN_TIME
		elif e < MID2_TIME:
			return MID1_TIME - BEGIN_TIME
		elif e < END_TIME:
			return MID1_TIME - BEGIN_TIME + e - MID2_TIME
		else:
			return MID1_TIME - BEGIN_TIME + END_TIME - MID2_TIME
	elif b < MID1_TIME:
		if e < MID1_TIME:
			return  e - b
		elif e < MID2_TIME:
			return MID1_TIME - b
		elif e < END_TIME:
			return MID1_TIME - b + e - MID2_TIME
		else:
			return MID1_TIME - b + END_TIME - MID2_TIME
	elif b < MID2_TIME:
		if e < MID2_TIME:
			return 0
		elif e < END_TIME:
			return e - MID2_TIME
		else:
			return END_TIME - MID2_TIME
	elif b < END_TIME:
		if e < END_TIME:
			return e - b
		else:
			return END_TIME - b

	return 0

def time_to_int(t):
	try:
		t = t.strip()
		tt = datetime.strptime(t, '%H:%M')
	except ValueError as e:
		print "can not convert value |%s| " % t
		raise ValueError("Can not convert")
	return tt.hour*60 + tt.minute

def resolv(file1):
	book = xlrd.open_workbook(file1)
	print "%r" % REPR(book.sheet_names())
	print book.biff_version, book.codepage, book.encoding

	sheet = book.sheet_by_index(0)

	print sheet.ncols, sheet.nrows
        out_file = os.path.join(os.path.dirname(file1), "out.csv")
        form = []
	with open(out_file, 'w') as f:
		for rx in xrange(2, sheet.nrows):
                        form_row = []
			for cx in xrange( sheet.ncols):
				cell = sheet.cell_value(rx, cx)
				if cx <2 or rx < 3:
					f.write(cell.encode("utf-8"))
					f.write(",\t")
                                        form_row.append(cell.encode("utf-8"))
					continue

				timelist = cell.split('\r\n')
				ms = check([time_to_int(x) for x in timelist if len(x) > 3])
				times = '|'.join([str(time_to_int(x)) for x in timelist if len(x) > 3])
				print "Column label at (rowx=%d, colx=%d) is %d" %\
					(rx, cx, ms)
				f.write("%d,\t" % (ms))
                                form_row.append(ms)
			f.write("\n")
                        form.append(form_row)

        return "out.csv", form

if __name__ == '__main__':
	book = xlrd.open_workbook('./data.xls')
	print "%r" % REPR(book.sheet_names())
	print book.biff_version, book.codepage, book.encoding

	sheet = book.sheet_by_index(0)

	print sheet.ncols, sheet.nrows
        form = []
	with open('out.csv', 'w') as f:
		for rx in xrange( 2, sheet.nrows):
                        form_row = []
			for cx in xrange( sheet.ncols):
				cell = sheet.cell_value(rx, cx)
				if cx < 2 or rx < 3:
                                        print "row: %d col: %d val: %s" % (rx, cx, cell.encode("utf-8"))
					f.write(cell.encode("utf-8"))
					f.write(",\t")
                                        form_row.append(cell.encode('utf-8'))
					continue

				timelist = cell.split('\r\n')
				ms = check([time_to_int(x) for x in timelist if len(x) > 3])
				times = '|'.join([str(time_to_int(x)) for x in timelist if len(x) > 3])
				print "Column label at (rowx=%d, colx=%d) is %d" %\
					(rx, cx, ms)
				f.write("%d,\t" % (ms))
                                form_row.append(ms)
			f.write("\n")
                        form.append(form_row)
