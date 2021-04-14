import gemmi
import os
from pathlib import Path


def get_table(block):
    for x in block:
        table = x.loop

    tags = table.tags
    table = block.find(tags)

    return table, tags


def update_star(starfile, ice_groups):
    in_doc = gemmi.cif.read_file(starfile)
    block_optics = in_doc.find_block('optics')
    block = in_doc.find_block('particles')
    new_document = gemmi.cif.Document()
    block_one_optics = new_document.add_new_block('optics')
    block_one = new_document.add_new_block('particles')

    table_optics, tags_optics = get_table(block_one_optics)  # optics
    loop = block_one.init_loop('', tags_optics)  # make temp new table
    for row in table_optics:
        loop.add_row(list(row))

    table, tags = get_table(block_one)  # particles

    # add new tag: named this to work in relion, but really it is
    # ice group for each particle (_ibIceGroup)
    #tags.append('_rlnHelicalTubeID')
    tags.append('_ibIceGroup')
    loop = block_one.init_loop('', tags)  # make temp new table
    for i in range(len(table)):
        row = table[i]
        new_row = list(row)
        new_row.append(f'{ice_groups[i]}')
        loop.add_row(new_row)  # update temp new table with all data

    new_document.write_file('particles.star')


def mic_star(starfile, job, mode):
    in_doc = gemmi.cif.read_file(starfile)
    block = in_doc.find_block('micrographs')
    new_document = gemmi.cif.Document()
    block_one = new_document.add_new_block('micrographs')
    for x in block:
        table = x.loop

    tags = table.tags
    tags.remove('_rlnMicrographName')
    table = block.find(tags)
    column = block.find(['_rlnMicrographName'])

    tags.insert(0, '_rlnMicrographName')

    loop = block_one.init_loop('', tags)  # make temp new table
    for i in range(len(table)):
        row = table[i]
        new_row = list(row)
        mic_name = list(column[i])[0]
        path_head, path_tail = os.path.split(mic_name)
        mic_name2 = Path(mic_name).parts
        #mic_name_new = os.path.join(mic_name2[-2], mic_name2[-1][:-4] + f'_{mode}ed.mrc')
         
        mic_name_new = os.path.join(path_head, path_tail[:-4] + f'_{mode}ed.mrc')
        new_row.insert(0, os.path.join(job, mic_name_new))
        
        loop.add_row(new_row)  # update temp new table with all data

    new_document.write_file(f'{mode}ed_micrographs.star')


if __name__ == '__main__':
    starfile = '/home/lexi/Documents/Diamond/ICEBREAKER/test_data/corrected_micrographs.star'
    job = 'External'
    mode = 'flatten'
    mic_star(starfile, job, mode)
