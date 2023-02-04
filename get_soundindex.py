def get_soundindex(distance, soundsettings):
    if not soundsettings["mindistance"] <= distance <= soundsettings["maxdistance"]:
        return None
    return int( soundsettings["magnitude"] * ( (distance - soundsettings["mindistance"]) 
                                              / (soundsettings["maxdistance"] - soundsettings["mindistance"]))
                                              **soundsettings["smoothen"] )
