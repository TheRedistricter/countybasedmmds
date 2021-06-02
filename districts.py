import codecs
from us_state_abbrev import us_state_abbrev
from mdutils.mdutils import MdUtils
import metis

combos = []


def findCombinationsUtil(arr, index, num, reducedNum):
    global combos
    if (reducedNum < 0):
        return

    if (reducedNum == 0):                              
        #for i in range(index):
        #    print(arr[i], end = " ")
        #print("")
        combos.append(arr[:index])
        return
                                                                           
    prev = 1 if(index == 0) else arr[index - 1]
    for k in range(prev, num + 1):
        arr[index] = k
        findCombinationsUtil(arr, index + 1, num, reducedNum - k)
                                                                    
def findCombinations(n):
    arr = [0] * n
    findCombinationsUtil(arr, 0, n, n)

def create_adj_list(adj_by_county, pop_by_county):
    adj_list = []
    pop_list = []
    county_by_index = {}
    sorted_county_names = sorted(pop_by_county.keys())
    index_by_county = {}
    for index, county in enumerate(sorted_county_names):
        index_by_county[county] = index
        county_by_index[index] = county

    indexed_pop_by_county = {}
    for county in pop_by_county.keys():
        indexed_pop_by_county[index_by_county[county]] = pop_by_county[county]

    indexed_adj_by_county = {}
    for county in adj_by_county.keys():
        adj_counties =  adj_by_county[county]
        indexed_adjacent_counties = []
        for adj_county in adj_counties:
            indexed_adjacent_counties.append(index_by_county[adj_county])
        indexed_adj_by_county[index_by_county[county]] = indexed_adjacent_counties

    for index in indexed_adj_by_county.keys():
        county = county_by_index[index]
        indexed_adjacent_counties = indexed_adj_by_county[index]
        adj_counties = []
        for indexed_adj_county in indexed_adjacent_counties:
             adj_counties.append(county_by_index[indexed_adj_county])
        
    for index in sorted(indexed_adj_by_county.keys()):
        adj_list.append(tuple(indexed_adj_by_county[index]))

    for index in sorted(indexed_pop_by_county.keys()):
        pop_list.append(indexed_pop_by_county[index])

    return adj_list, pop_list, county_by_index

def partition_districts(adj_by_county, pop_by_county, tpwgts):
    (adj_list, pop_list, county_by_index) = create_adj_list(adj_by_county, pop_by_county)
 
    valid = True
    for county in adj_by_county.keys():
        if county not in pop_by_county:
            print('{} is in adj_by_county but not in pop_by_county'.format(county))
            valid = False
    for county in pop_by_county.keys():
        if county not in adj_by_county:
            print('{} is in pop_by_county but not in adj_by_county'.format(county))
            valid = False

    if not valid:
        exit()
    
    G = metis.adjlist_to_metis(adj_list, nodew=pop_list)

    options = {}
    options['contig'] = True

    (edgecuts, parts) = metis.part_graph(G, len(tpwgts), tpwgts, **options)

    (adj_counties_by_district, county_pop_by_district) = create_districts(parts, adj_list, county_by_index, pop_list)

    return adj_counties_by_district, county_pop_by_district

def create_districts(parts, adj_list, county_by_index, pop_list):
    adj_counties_by_district = {}
    county_pop_by_district = {}
    
    for index, district in enumerate(parts):
        if district not in adj_counties_by_district:
             adj_counties_by_district[district] = {}
             county_pop_by_district[district] = {}
        adj_counties = adj_counties_by_district[district]
        county_pops = county_pop_by_district[district]
        county = county_by_index[index]
        adj_counties[county] = []
        adj_county_indexes = adj_list[index]
        for adj_index in adj_county_indexes:
             adj_counties[county].append(county_by_index[adj_index])
        county_pops[county] = pop_list[index]
        adj_counties_by_district[district] = adj_counties
        county_pop_by_district[district] = county_pops

    for district in adj_counties_by_district.keys():
        adj_counties = adj_counties_by_district[district]
        for county in adj_counties.keys():
            adj_county_list = adj_counties[county]
            new_adj_county_list = []
            for adj_county in adj_county_list:
                if adj_county in new_adj_county_list:
                    new_adj_county_list.append(adj_county)
            adj_counties[county] = new_adj_county_list
        adj_counties_by_district[district] = adj_counties
        
    return adj_counties_by_district, county_pop_by_district

def verify_adjs(adjs_by_county_by_state_abbr):
    verified = True
    for state_abbr in adjs_by_county_by_state_abbr.keys():
        adjs_by_county = adjs_by_county_by_state_abbr[state_abbr]
        for county in adjs_by_county.keys():
            adj_counties = adjs_by_county[county]
            if len(adj_counties) == 0:
                print('{} in {} has no adjacent counties'.format(county, state_abbr))
                verified = False
    return verified

def describe_district(district_pops, num_reps, target_pop):
    district_pop = 0
    counties = []
    for county, county_pop in district_pops.items():
        counties.append(county)
        district_pop += county_pop
    pop_per_rep = district_pop//reps_per_district
    deviation_pct = abs(100 - int(pop_per_rep/target_pop*100.0))
    print('{} reps consisting of {} has a pop per rep of {} which is {}% off target'.format(num_reps, counties, pop_per_rep, deviation_pct))
    return counties, pop_per_rep, deviation_pct

mdFile = MdUtils(file_name='index',  title='County-based multi-member Congressional districts')

mdFile.new_header(level=1, title='Assumptions')
mdFile.new_paragraph("Congressional districts are contiguous, compact, and of equivalent population.")
mdFile.new_paragraph("County boundaries delimit US Congressional districts.")
mdFile.new_paragraph("Congressional districts have one or more members.")
mdFile.new_header(level=1, title='Approach')
mdFile.new_paragraph("Exhaustively specify every combination of single and multi-member districts.")
mdFile.new_paragraph("Partition the graph of a State's adjacent counties into contiguous single and multi-member districts.")
mdFile.new_paragraph('Prefer districts with fewer members.')
mdFile.new_paragraph("Prefer districts with smallest deviation in population from average.")
mdFile.new_paragraph("Multi-member districts would use either single transferrable vote or single non-transferable vote.")
mdFile.new_header(level=1, title='Code')
mdFile.new_paragraph('https://github.com/TheRedistricter/countybasedmmds')
mdFile.new_header(level=1, title='Results')

reps_by_state_abbr = {}
reps_f = open('reps_by_state.txt', 'r')
reps_lines = reps_f.readlines()
for reps_line in reps_lines:
    [state, reps_str] = reps_line.split(',')
    state_abbr = us_state_abbrev[state]
    reps_by_state_abbr[state_abbr] = int(reps_str)

adj_f = codecs.open('county_adjacency.txt', 'r', 'iso-8859-1')
current_state_abbr = ''
current_county = ''
county_adj_lines = adj_f.readlines()
adjs_by_county_by_state_abbr = {}
for county_adj_line in county_adj_lines:
    fields = county_adj_line.split('\t')
    first_field = fields[0]
    if first_field != '':
        [current_county, current_state_abbr] = first_field.split(',')
        current_county = current_county.replace('"', '').strip()
        current_state_abbr = current_state_abbr.replace('"', '').strip()
        if current_state_abbr not in adjs_by_county_by_state_abbr:
             adjs_by_county_by_state_abbr[current_state_abbr] = {}
        adjs_by_county = adjs_by_county_by_state_abbr[current_state_abbr]
        if current_county not in adjs_by_county:
            adjs_by_county[current_county] = []
        adjs_by_county_by_state_abbr[current_state_abbr] = adjs_by_county
    [county, state_abbr] = fields[2].split(",")
    county = county.replace('"', '').strip()
    state_abbr = state_abbr.replace('"', '').strip()
    if state_abbr == current_state_abbr:
        if county != current_county:
            adjs_by_county = adjs_by_county_by_state_abbr[current_state_abbr]
            adjs = adjs_by_county[current_county]
            adjs.append(county)
            adjs_by_county[current_county] = adjs
            adjs_by_county_by_state_abbr[current_state_abbr] = adjs_by_county

states_to_remove = []
for state_abbr in adjs_by_county_by_state_abbr:
    if state_abbr not in reps_by_state_abbr:
        states_to_remove.append(state_abbr)
#for state_abbr in reps_by_state_abbr:
#    if reps_by_state_abbr[state_abbr] < 2:
#        states_to_remove.append(state_abbr)
for state_abbr in states_to_remove:
    del adjs_by_county_by_state_abbr[state_abbr]
for state_abbr in states_to_remove:
    if state_abbr in reps_by_state_abbr:
        del reps_by_state_abbr[state_abbr]
#del adjs_by_county_by_state_abbr['HI']
#del reps_by_state_abbr['HI']

#if not verify_adjs(adjs_by_county_by_state_abbr):
#    print('Adjs not verified')
#    exit()

pop_by_county_by_state_abbr = {}
pop_by_state_abbr = {}
pop_f = codecs.open('county_pops.txt', 'r', 'iso-8859-1')
pop_lines = pop_f.readlines()

for pop_line in pop_lines:
    [state, county, county_pop_str] = pop_line.split(",")
    state_abbr = us_state_abbrev[state]
    county_pop = int(county_pop_str)
    if state == county:
        pop_by_state_abbr[state_abbr]=county_pop
    else:
        if state_abbr not in pop_by_county_by_state_abbr:
            pop_by_county_by_state_abbr[state_abbr] = {}
        pop_by_county = pop_by_county_by_state_abbr[state_abbr]
        pop_by_county[county] = county_pop
        pop_by_county_by_state_abbr[state_abbr] = pop_by_county

for state_abbr, num_reps in reps_by_state_abbr.items():
    mdFile.new_header(level=2, title=state_abbr)
    print('==================== {} ============================='.format(state_abbr))
    adj_by_county = adjs_by_county_by_state_abbr[state_abbr]
    pop_by_county = pop_by_county_by_state_abbr[state_abbr]
    combos = []
    if num_reps > 1 and state_abbr != 'HI':
        findCombinations(num_reps);
    best_combo = [num_reps]
    best_combo_score = num_reps
    best_desc_by_district = {}
    best_desc_by_district[0] = (num_reps, list(pop_by_county.keys()), pop_by_state_abbr[state_abbr]//num_reps , 0)
    for combo in combos:
        desc_by_district = {}
        print('Combo: {}'.format(combo))
        tpwgts = []
        for num in combo:
            tpwgts.append(num/num_reps)
        if len(tpwgts) > 1:
            (adj_counties_by_district, county_pop_by_district) = partition_districts(adj_by_county, pop_by_county, tpwgts)
            worst_deviation_pct = 0
            worst_num_reps = 1
            num_districts= len(adj_counties_by_district.keys())
            num_combos = len(combo)
            if num_districts != num_combos:
                continue
            for district in county_pop_by_district.keys():
                district_pops = county_pop_by_district[district]
                reps_per_district = tpwgts[district]*num_reps
                if reps_per_district > worst_num_reps:
                    worst_num_reps = reps_per_district
                print('District {}:'.format(district))
                (counties, pop_per_rep, deviation_pct) = describe_district(district_pops, reps_per_district, pop_by_state_abbr[state_abbr]//num_reps)
                desc_by_district[district] = (reps_per_district, counties, pop_per_rep, deviation_pct)
                if deviation_pct > worst_deviation_pct:
                    worst_deviation_pct = deviation_pct
                print('...')
            combo_score = worst_num_reps +  worst_deviation_pct
            print('Score for {} is {}'.format(combo, combo_score))
            if (combo_score < best_combo_score) or ((combo_score == best_combo_score) and (len(combo) > len(best_combo))):
                best_combo_score = combo_score
                best_combo = combo
                best_desc_by_district = {}
                for district in desc_by_district.keys():
                    best_desc_by_district[district] = desc_by_district[district]
                
            print('=================================================')
    print('Best combo for {} is  {} with score {}'.format(state_abbr, best_combo, best_combo_score))
    list_of_strings = ["District", "Representatives", "Pop. per rep.", "Deviation %", "Counties"]
    for district in sorted(best_desc_by_district.keys()):
        (reps_per_district, counties, pop_per_rep, deviation_pct) = best_desc_by_district[district]
        list_of_strings.append(str(district+1))
        list_of_strings.append(str(int(reps_per_district)))
        list_of_strings.append(str(int(pop_per_rep)))
        list_of_strings.append(str(deviation_pct)+'%')
        list_of_strings.append(counties[0])
        for county in counties[1:]:
            list_of_strings.append('')
            list_of_strings.append('')
            list_of_strings.append('')
            list_of_strings.append('')
            list_of_strings.append(county)
    mdFile.new_table(columns=5, rows=len(pop_by_county.keys())+1, text=list_of_strings, text_align='left')

mdFile.create_md_file() 
