settings = {
    "type_options": ["cpu", "gpu"],
    # A dictionary mapping a type option to the type that it appears as in the query
    "type_strings": {
        "cpu": "cpu",
        "gpu": "nvidia_com_gpu"
    },
    # The string in the query to be replaced with whatever type of data we're retrieving
    "type_string_identifier": "%TYPE_STRING%",
    # Analysis options, the types are the required types to perform the analysis.
    # Methods are filled out by analysis.py on the analysis() call
    # Requirements are fulfilled in the analysis() call
    "analysis_options": {
        "cpuhours": {
            "types": ["cpu"],
            "requires": [],
            "method": None
        },
        "cpuhourstotal": {
            "types": ["cpu"],
            "requires": ["cpuhours"],
            "method": None
        },
        "cpujobs": {
            "types": ["cpu"],
            "requires": ["gpujobs"],
            "method": None
        },
        "cpujobstotal": {
            "types": ["cpu"],
            "requires": ["cpujobs"],
            "method": None,
        },
        "gpuhours": {
            "types": ["gpu"],
            "requires": [],
            "method": None
        },
        "gpuhourstotal": {
            "types": ["gpu"],
            "requires": ["gpuhours"],
            "method": None
        },
        "gpujobs": {
            "types": ["gpu"],
            "requires": [],
            "method": None,
        },
        "gpujobstotal": {
            "types": ["gpu"],
            "requires": ["gpujobs"],
            "method": None,
        },
        "uniquenslist": {
            "types": ["cpu", "gpu"],
            "requires": [],
            "method": None
        },
        "uniquens": {
            "types": ["cpu", "gpu"],
            "requires": ["uniquenslist"],
            "method": None
        },
        "jobstotal": {
            "types": ["cpu", "gpu"],
            "requires": ["cpujobstotal", "gpujobstotal"],
            "method": None
        }
    }
}