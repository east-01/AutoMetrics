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
            "vis_options": {
                "type": "horizontalbar",
                "title": "Total CPU Hours by Namespace from %MONTH%",
                "subtext": "Total CPU Hours: %TOTCPUHRS%",
                "color": "skyblue",
                "variables": {
                    "TOTCPUHRS": "cpuhourstotal"
                }
            }
        },
        "cpuhourstotal": {
            "types": ["cpu"],
            "requires": ["cpuhours"]
        },
        "cpujobs": {
            "types": ["cpu"],
            "requires": ["gpujobs"],
            "vis_options": {
                "type": "horizontalbar",
                "title": "Total CPU Jobs by Namespace from %MONTH%",
                "subtext": "Total CPU Jobs: %TOTCPUJOBS%",
                "color": "skyblue",
                "variables": {
                    "TOTCPUJOBS": "cpujobstotal"
                }
            }
        },
        "cpujobstotal": {
            "types": ["cpu"],
            "requires": ["cpujobs"]
        },
        "gpuhours": {
            "types": ["gpu"],
            "requires": [],
            "vis_options": {
                "type": "horizontalbar",
                "title": "Total GPU Hours by Namespace from %MONTH%",
                "subtext": "Total GPU Hours: %TOTGPUHRS%",
                "color": "orange",
                "variables": {
                    "TOTGPUHRS": "gpuhourstotal"
                }
            }
        },
        "gpuhourstotal": {
            "types": ["gpu"],
            "requires": ["gpuhours"]
        },
        "gpujobs": {
            "types": ["gpu"],
            "requires": [],
            "vis_options": {
                "type": "horizontalbar",
                "title": "Total GPU Jobs by Namespace from %MONTH%",
                "subtext": "Total GPU Jobs: %TOTGPUJOBS%",
                "color": "orange",
                "variables": {
                    "TOTGPUJOBS": "gpujobstotal"
                }
            }
        },
        "gpujobstotal": {
            "types": ["gpu"],
            "requires": ["gpujobs"]
        },
        "uniquenslist": {
            "types": ["cpu", "gpu"],
            "requires": []
        },
        "uniquens": {
            "types": ["cpu", "gpu"],
            "requires": ["uniquenslist"]
        },
        "jobstotal": {
            "types": ["cpu", "gpu"],
            "requires": ["cpujobstotal", "gpujobstotal"]
        }
    },
    "vizualization_analyses": ["gpujobs", "gpuhours", "cpujobs", "cpuhours"]
}