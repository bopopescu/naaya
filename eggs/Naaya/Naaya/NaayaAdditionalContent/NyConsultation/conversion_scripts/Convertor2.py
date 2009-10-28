from BeautifulSoup import BeautifulSoup, Tag
from soupselect import select
import re

def remove_align_left_from_images(soup):
    imgs_aligned_left = soup.findAll('img', align=re.compile('left', re.IGNORECASE))

    for img in imgs_aligned_left:
        del img['align']





def remove_style_from_tags(soup, pattern):
    for tag in soup.findAll(style=pattern):
        tag['style'] = re.sub(pattern, '', tag['style'])

def remove_absolute_position_from_tags(soup):
    pattern = re.compile('position: absolute;')
    remove_style_from_tags(soup, pattern)

def remove_line_height_from_tags(soup):
    pattern = re.compile('line-height: \d.\d{1,2}in')
    remove_style_from_tags(soup, pattern)





def insert_front_path_for_images(soup, path):
    imgs = soup.findAll('img')
    for img in imgs:
        img['src'] = path + img['src']

def scale_all_images(soup, multiplier):
    imgs = soup.findAll('img')
    for img in imgs:
        if img.has_key('width') and img.has_key('height'):
            img['width'] = str(int(multiplier * int(img['width'])))
            img['height'] = str(int(multiplier * int(img['height'])))




def get_tag_text(tag):
    ret = ''
    for t in tag.contents:
        if isinstance(t, Tag):
            ret += get_tag_text(t)
        else:
            ret += t
    return ret

def get_item_text(item):
    if isinstance(item, Tag):
        return get_tag_text(item)
    return str(item)

def get_section_title(h1_tag):
    return get_tag_text(h1_tag).strip().replace('\n', ' ')

def get_first_tag_child(tag):
    for item in tag.contents:
        if isinstance(item, Tag):
            return item
    return None

def tag_has_only_tag_child(tag, child_name):
    if len(tag.contents) == 0 or len(tag.contents) > 3:
        return False

    child_tag = get_first_tag_child(tag)
    if not isinstance(child_tag, Tag):
        return False

    return child_tag.name == child_name

def get_sections_h1_tags(soup):
    ret = []

    # find h1 tags
    for tag in soup.findAll('h1'):
        section_title = get_section_title(tag)
        if section_title != '':
            ret.append(tag)

    # find heading tags otherwise
    if ret == []:
        selector = 'body p font[size="3"] font b'
        #ret = select(soup, selector)
    selector = 'body p[class="western"] font b'
    #ret = select(soup, selector)
    #print [str(tag) for tag in select(soup, selector)]

    return ret

def get_sections_titles(soup):
    return [get_section_title(h1_tag) for h1_tag in get_sections_h1_tags(soup)]

def get_top_tag(tag):
    ret = tag

    while ret.parent.name != 'body':
        ret = ret.parent

    return ret

def get_section_split_tags(h1_tags):
    ret = []

    for h1_tag in h1_tags:
        tag = get_top_tag(h1_tag)
        ret.append(tag)

    return ret

def split_sections(soup):
    title = soup.html.head.title.string

    h1_tags = get_sections_h1_tags(soup)
    sections_titles = [get_section_title(h1_tag) for h1_tag in h1_tags]

    section_splits = get_section_split_tags(h1_tags)

    # split the soup in sections
    sections = []
    current_section = []
    for item in soup.html.body:
        if item in section_splits:
            sections.append(current_section)
            current_section = []
        else:
            current_section.append(item)
    sections.append(current_section)
    sections.pop(0) # remove the first one


    # maybe get title from first section
    s = sections[0]
    string_s = ''
    for item in s[1:]:
        string_s += get_item_text(item)
    if string_s.strip() == '':
        sections.pop(0)
        title = sections_titles.pop(0)

    # convert sections to strings
    sections_strings = []
    for s in sections:
        sections_strings.append(''.join([str(item) for item in s]))

    return title, sections_titles, sections_strings




def find_footnotes_and_anchors(soup):
    selector = '.sdfootnoteanc'
    footnote_anchors = select(soup, selector)
    #print '\n'.join([str(anc) for anc in footnote_anchors])

    footnotes = []
    for i in range(len(footnote_anchors)):
        selector = '#sdfootnote%s' % (i+1)
        footnotes.extend(select(soup, selector))
    #print '\n'.join([str(f) for f in footnotes])

    return footnote_anchors, footnotes

def remove_footnotes_from_last_section(sections_strings):
    last_ss = sections_strings[-1]
    last_ssoup = BeautifulSoup(last_ss)

    last_ssfootnotes = []
    for i in range(len(footnote_anchors)):
        selector = '#sdfootnote%s' % (i+1)
        last_ssfootnotes.extend(select(soup, selector))

    for f in last_ssfootnotes:
        f.extract()

def add_footnotes_to_sections(sections_strings, footnote_anchors, footnotes):
    j = 0
    for i, ss in enumerate(sections_strings):
        ssoup = BeautifulSoup(ss)
        selector = '.sdfootnoteanc'
        footnote_anchors = select(ssoup, selector)
        #print 'For section ', i, ' found footnotes ', '\n'.join([str(anc) for anc in footnote_anchors])

        for k in range(len(footnote_anchors)):
            anchor = footnote_anchors[k]
            footnote = footnotes[j]

            if '#' + anchor['name'] == footnote.p.a['href'] and '#' + footnote.p.a['name'] == anchor['href']:
                print 'Found match for footnote', j, ' in section ', i, ' anchor ', k
            else:
                print 'ERROR: wrong match for footnote', j, ' with anchor ', k, ' from section ', i

            sections_strings[i] = sections_strings[i] + str(footnote)

            j += 1



def propagate_styles(soup):
    style_contents = str(soup.html.head.style.contents[0])
    styles = style_contents.split('\n')
    for s in styles:
        s = s.strip()
        if s == '' or s == '<!--' or s == '-->':
            continue
        if s.startswith('@page'):
            continue
        selector, rest = s.split('{', 1)
        style = rest.split('}', 1)[0]
        for tag in select(soup, selector.lower()):
            if tag.has_key('style'):
                tag['style'] += style
            else:
                tag['style'] = style

if __name__ == '__main__':
    from sys import argv, exit

    if len(argv) != 3:
        print 'USAGE: python %s <input-html> <output-html>' % argv[0]
        exit(255)

    fd = open(argv[1], 'r')
    htmldoc = fd.read()
    fd.close()

    soup = BeautifulSoup(htmldoc)

    propagate_styles(soup)
    remove_align_left_from_images(soup)
    remove_absolute_position_from_tags(soup)
    remove_line_height_from_tags(soup)
    insert_front_path_for_images(soup, 'images/')
    scale_all_images(soup, 1.5)

    footnote_anchors, footnotes = find_footnotes_and_anchors(soup)
    try:
        title, sections_titles, sections_strings = split_sections(soup)

        remove_footnotes_from_last_section(sections_strings)
        add_footnotes_to_sections(sections_strings, footnote_anchors, footnotes)

        print 'found title:', title
        for i, s in enumerate(sections_strings):
            print 'found section.%d title:' % i, sections_titles[i]
            fd = open('section.%d.html' % i, 'w')
            fd.write(s)
            fd.close()
    except IndexError, e:
        print 'Could not split into sections'


    fd = open(argv[2], 'w')
    fd.write(soup.prettify())
    fd.close()

