from datetime import datetime
from django import template

register = template.Library()


class Cell:

    def __init__(self, val, color):
        self.val = val
        self.color = color

    def __repr__(self):
        return self.val

    def __str__(self):
        return str(self.val)

@register.inclusion_tag("xls/includes/display_form.html")
def display_form(form, t="time"):
    new_form = []
    if t == "time":
        for row in form:
            new_row = []
            for c in row:
                if c <= 190:
                    new_row.append(Cell(c, "red"))
                else:
                    new_row.append(Cell(c, "black"))
            new_form.append(new_row)
    else:
        format1 = "%H:%M"
        dt1 = datetime.strptime("11:45", format1)
        dt2 = datetime.strptime("12:30", format1)

        for row in form:
            new_row = []
            for col in row:
                color1 = "black"
                if len(col) > 5 and col[2] == ":":
                    for c in col.split():
                        dt = datetime.strptime(c, format1)
                        if dt >= dt1 and dt <= dt2:
                            color1 = "green"
                    new_row.append(Cell(col, color1))
                else:
                    new_row.append(Cell(col, color1))
            new_form.append(new_row)

    return {'form': new_form}
