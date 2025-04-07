# from data.identifiers.identifier import SourceIdentifier
from data.filters import filter_source_type, filter_analyis_type

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
    "analysis_settings": {
        "cpuhours": {
            "filter": filter_source_type("cpu"),
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
            "filter": filter_analyis_type("cpuhours"),
            "requires": ["cpuhours"]
        },
        "cpujobs": {
            "filter": filter_source_type("cpu"),
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
            "filter": filter_analyis_type("cpujobs"),
            "requires": ["cpujobs"]
        },
        "gpuhours": {
            "filter": filter_source_type("gpu"),
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
            "filter": filter_analyis_type("gpuhours"),
            "requires": ["gpuhours"]
        },
        "gpujobs": {
            "filter": filter_source_type("gpu"),
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
            "filter": filter_analyis_type("gpujobs"),
            "requires": ["gpujobs"]
        },
        "jobstotal": {
            "filter": filter_analyis_type("cpujobstotal"),
            "requires": ["cpujobstotal", "gpujobstotal"]
        }#,
        # "cvgpuhours": {
        #     "filter": None,
        #     "requires": ["cpuhourstotal", "gpuhourstotal"],
        #     "vis_options": {
        #         "type": "timeseries",
        #         "title": "CPU and GPU hours by month",
        #         "colors": {
        #             "cpuhourstotal": "red",
        #             "gpuhourstotal": "blue"
        #         }
        #     }
        # },
        # "cvgpujobs": {
        #     "filter": None,
        #     "requires": ["cpujobstotal", "gpujobstotal"],
        #     "vis_options": {
        #         "type": "timeseries",
        #         "title": "CPU and GPU jobs by month",
        #         "colors": {
        #             "cpujobstotal": "red",
        #             "gpujobstotal": "blue"
        #         }
        #     }
        # }
    }
}