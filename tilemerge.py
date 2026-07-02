"""Merging of individual level tiles into larger rectangles, so that a run of
   adjacent platform tiles can become one big Platform object instead of many
   small ones. Kept free of pygame imports so it can be tested standalone."""

def merge_cells(cells):
    """Merges a collection of (column, row) tile coordinates into a list of
       (column, row, width, height) rectangles (all in whole tiles) that
       exactly cover the given cells without overlapping.

       Greedy, two passes: adjacent cells within a row are first merged into
       horizontal runs, then runs with identical horizontal extents in
       consecutive rows are merged into taller rectangles."""
    columns_by_row = {}
    for column, row in cells:
        columns_by_row.setdefault(row, set()).add(column)

    rectangles = []
    previous_row = None
    previous_runs = {} #Maps (column, width) to the rectangle ending at previous_row
    for row in sorted(columns_by_row):
        #Merge adjacent cells into horizontal runs of [column, width]
        runs = []
        for column in sorted(columns_by_row[row]):
            if runs and column == runs[-1][0] + runs[-1][1]:
                runs[-1][1] += 1
            else:
                runs.append([column, 1])
        #Extend any matching rectangle from the row above; otherwise start a
        #new one
        current_runs = {}
        for column, width in runs:
            rectangle = previous_runs.get((column, width))
            if rectangle is not None and previous_row == row - 1:
                rectangle[3] += 1
            else:
                rectangle = [column, row, width, 1]
                rectangles.append(rectangle)
            current_runs[(column, width)] = rectangle
        previous_row = row
        previous_runs = current_runs
    return [tuple(r) for r in rectangles]
