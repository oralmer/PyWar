def do_turn(strategic):
    my_country = strategic.get_my_country()
    all_countries = strategic.list_all_countries()
    other_countries = [country for country in all_countries if country != my_country]
    strategic.conquer_using_tanks_tile_of(other_countries)
