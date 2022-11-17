# elid_page_display
# Take a range object and return a list of elided numbers.
# TODO: Remove this. This app was ported from Django 2.2 where Paginator.get_elided_page_range() did not exist.

def elid_page_display(page_range, number, on_each_side=3, on_ends=2):
    # Initialize
    page_list = list(page_range)

    if number not in page_list:
        raise Exception("Number is not in page list.")

    begin = []
    middle = []
    end = []

    # begin list.
    for i in range(0, on_ends):
        if i >= len(page_list): # Reached the end of the list.
            break

        begin.append(page_list[i])

    # end list.
    end_idx = len(page_list)-1
    for i in range(end_idx, end_idx-on_ends, -1):
        if i < 0: # Reached the beginning of the list.
            break

        end.insert(0, page_list[i])
    after_begin = page_list[on_ends] if on_ends <= end_idx else page_list[end_idx]
    before_end = page_list[end_idx-on_ends] if on_ends <= end_idx else page_list[0]

    # middle list.
    # Get range around index where the number of the list is.
    num_idx = page_list.index(number)
    for i in range(num_idx-on_each_side, num_idx+on_each_side+1):
        if i >=0 and i <= end_idx:
            middle.append(page_list[i])

    # Build the ellipsed list.
    elid_list = begin

    # Check if the next number after begin is in the middle. If not, add an ellipsis and the entire middle.
    if (after_begin not in middle) and (elid_list[len(elid_list)-1] not in middle):
        elid_list.append("...")
        elid_list.extend(middle)
    else:
        for num in middle:
            if num not in elid_list:
                elid_list.append(num)
    
    # Check if the next number before end is in the middle. If not, add an ellipsis and the entire end.
    if (before_end not in middle) and (elid_list[len(elid_list)-1] not in end):
        elid_list.append("...")
        elid_list.extend(end)
    else:
        for num in end:
            if num not in elid_list:
                elid_list.append(num)

    return elid_list

if __name__ == "__main__":
    # print(elid_page_display(range(1,21), 10))
    # print(elid_page_display(range(1,21), 10, 0, 3))
    # print(elid_page_display(range(1,21), 3, 2))
    for i in range(1, 21):
        print(elid_page_display(range(1, 21), i, 1, 2))
    # print(elid_page_display(range(1,5), 2))