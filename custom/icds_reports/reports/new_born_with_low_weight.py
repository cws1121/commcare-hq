from collections import OrderedDict, defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, rrule
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _

from custom.icds_reports.cache import icds_quickcache
from custom.icds_reports.const import LocationTypes, ChartColors, MapColors, AggregationLevels
from custom.icds_reports.models import AggChildHealthMonthly, ChildHealthMonthlyView
from custom.icds_reports.utils import apply_exclude, generate_data_for_map, chosen_filters_to_labels, \
    indian_formatted_number, get_filters_from_config_for_chart_view
from custom.icds_reports.messages import new_born_with_low_weight_help_text
from custom.icds_reports.utils import get_location_launched_status


@icds_quickcache(['domain', 'config', 'loc_level', 'show_test', 'icds_features_flag'], timeout=30 * 60)
def get_newborn_with_low_birth_weight_map(domain, config, loc_level, show_test=False, icds_features_flag=False):
    config['month'] = datetime(*config['month'])

    def get_data_for(filters):
        queryset = AggChildHealthMonthly.objects.filter(
            **filters
        ).values(
            '%s_name' % loc_level, '%s_map_location_name' % loc_level
        ).annotate(
            low_birth=Sum('low_birth_weight_in_month'),
            in_month=Sum('weighed_and_born_in_month'),
            all=Sum('born_in_month')
        ).order_by('%s_name' % loc_level, '%s_map_location_name' % loc_level)
        if not show_test:
            queryset = apply_exclude(domain, queryset)
        return queryset

    if icds_features_flag:
        location_launched_status = get_location_launched_status(config, loc_level)
    else:
        location_launched_status = None
    data_for_map, in_month_total, low_birth_total, average, total = generate_data_for_map(
        get_data_for(config),
        loc_level,
        'low_birth',
        'in_month',
        20,
        60,
        'all',
        location_launched_status=location_launched_status
    )

    fills = OrderedDict()
    fills.update({'0%-20%': MapColors.PINK})
    fills.update({'20%-60%': MapColors.ORANGE})
    fills.update({'60%-100%': MapColors.RED})
    if icds_features_flag:
        fills.update({'Not Launched': MapColors.GREY})
    fills.update({'defaultFill': MapColors.GREY})

    gender_ignored, age_ignored, chosen_filters = chosen_filters_to_labels(config)

    return {
        "slug": "low_birth",
        "label": "Percent Newborns with Low Birth Weight{}".format(chosen_filters),
        "fills": fills,
        "rightLegend": {
            "average": average,
            "info": _((
                new_born_with_low_weight_help_text(html=True)
            )),
            "extended_info": [
                {
                    'indicator': 'Total Number of Newborns born in given month{}:'.format(chosen_filters),
                    'value': indian_formatted_number(total)
                },
                {
                    'indicator': 'Number of Newborns with LBW in given month{}:'.format(chosen_filters),
                    'value': indian_formatted_number(low_birth_total)
                },
                {
                    'indicator': 'Total Number of children born and weight in given month{}:'.format(
                        chosen_filters
                    ),
                    'value': indian_formatted_number(in_month_total)
                },
                {
                    'indicator': '% newborns with LBW in given month{}:'.format(chosen_filters),
                    'value': '%.2f%%' % (low_birth_total * 100 / float(in_month_total or 1))
                },
                {
                    'indicator': '% of children with weight in normal{}:'.format(chosen_filters),
                    'value': '%.2f%%' % ((in_month_total - low_birth_total) * 100 / float(in_month_total or 1))
                },
                {
                    'indicator': '% Unweighted{}:'.format(chosen_filters),
                    'value': '%.2f%%' % ((total - in_month_total) * 100 / float(total or 1))
                }
            ]

        },
        "data": dict(data_for_map),
    }


@icds_quickcache(['domain', 'config', 'loc_level', 'show_test', 'icds_features_flag'], timeout=30 * 60)
def get_newborn_with_low_birth_weight_chart(domain, config, loc_level, show_test=False, icds_features_flag=False):
    month = datetime(*config['month'])
    three_before = datetime(*config['month']) - relativedelta(months=3)

    config['month__range'] = (three_before, month)
    del config['month']

    # using child health monthly while querying for sector level due to performance issues
    if icds_features_flag and config['aggregation_level'] >= AggregationLevels.SUPERVISOR:
        chm_filter = get_filters_from_config_for_chart_view(config)
        chm_queryset = ChildHealthMonthlyView.objects.filter(**chm_filter)
    else:
        chm_queryset = AggChildHealthMonthly.objects.filter(**config)
    chart_data = chm_queryset.values(
        'month', '%s_name' % loc_level
    ).annotate(
        low_birth=Sum('low_birth_weight_in_month'),
        in_month=Sum('weighed_and_born_in_month'),
        all=Sum('born_in_month')
    ).order_by('month')

    if not show_test:
        chart_data = apply_exclude(domain, chart_data)

    data = {
        'blue': OrderedDict()
    }

    dates = [dt for dt in rrule(MONTHLY, dtstart=three_before, until=month)]

    for date in dates:
        miliseconds = int(date.strftime("%s")) * 1000
        data['blue'][miliseconds] = {'y': 0, 'in_month': 0, 'low_birth': 0, 'all': 0}

    best_worst = {}
    if icds_features_flag:
        if 'month' not in config:
            config['month'] = month
        location_launched_status = get_location_launched_status(config, loc_level)
    else:
        location_launched_status = None
    for row in chart_data:
        if location_launched_status:
            launched_status = location_launched_status.get(row['%s_name' % loc_level])
            if launched_status is None or launched_status <= 0:
                continue
        date = row['month']
        in_month = row['in_month'] or 0
        location = row['%s_name' % loc_level]
        low_birth = row['low_birth'] or 0
        all_birth = row['all'] or 0

        best_worst[location] = low_birth * 100 / float(in_month or 1)

        date_in_miliseconds = int(date.strftime("%s")) * 1000

        data_for_month = data['blue'][date_in_miliseconds]
        data_for_month['low_birth'] += low_birth
        data_for_month['in_month'] += in_month
        data_for_month['all'] += all_birth
        data_for_month['y'] = data_for_month['low_birth'] / float(data_for_month['in_month'] or 1)

    all_locations = [
        {
            'loc_name': key,
            'percent': val
        }
        for key, val in best_worst.items()
    ]
    all_locations_sorted_by_name = sorted(all_locations, key=lambda x: x['loc_name'])
    all_locations_sorted_by_percent_and_name = sorted(all_locations_sorted_by_name, key=lambda x: x['percent'])

    return {
        "chart_data": [
            {
                "values": [
                    {
                        'x': key,
                        'y': val['y'],
                        'in_month': val['in_month'],
                        'low_birth': val['low_birth'],
                        'all': val['all']
                    } for key, val in data['blue'].items()
                ],
                "key": "% Newborns with Low Birth Weight",
                "strokeWidth": 2,
                "classed": "dashed",
                "color": ChartColors.BLUE
            }
        ],
        "all_locations": all_locations_sorted_by_percent_and_name,
        "top_five": all_locations_sorted_by_percent_and_name[:5],
        "bottom_five": all_locations_sorted_by_percent_and_name[-5:],
        "location_type": loc_level.title() if loc_level != LocationTypes.SUPERVISOR else 'Sector'
    }


@icds_quickcache(['domain', 'config', 'loc_level', 'location_id', 'show_test', 'icds_features_flag'],
                 timeout=30 * 60)
def get_newborn_with_low_birth_weight_data(domain, config, loc_level, location_id,
                                           show_test=False, icds_features_flag=False):
    group_by = ['%s_name' % loc_level]

    config['month'] = datetime(*config['month'])
    data = AggChildHealthMonthly.objects.filter(
        **config
    ).values(
        *group_by
    ).annotate(
        low_birth=Sum('low_birth_weight_in_month'),
        in_month=Sum('weighed_and_born_in_month'),
        all=Sum('born_in_month')
    ).order_by('%s_name' % loc_level)

    if not show_test:
        data = apply_exclude(domain, data)

    chart_data = {
        'blue': [],
    }

    tooltips_data = defaultdict(lambda: {
        'in_month': 0,
        'low_birth': 0,
        'all': 0
    })
    if icds_features_flag:
        location_launched_status = get_location_launched_status(config, loc_level)
    else:
        location_launched_status = None
    for row in data:
        if location_launched_status:
            launched_status = location_launched_status.get(row['%s_name' % loc_level])
            if launched_status is None or launched_status <= 0:
                continue
        in_month = row['in_month'] or 0
        name = row['%s_name' % loc_level]

        all_records = row['all'] or 0
        low_birth = row['low_birth'] or 0

        value = low_birth / float(in_month or 1)

        tooltips_data[name]['low_birth'] += low_birth
        tooltips_data[name]['in_month'] += in_month
        tooltips_data[name]['all'] += all_records

        chart_data['blue'].append([
            name, value
        ])

    chart_data['blue'] = sorted(chart_data['blue'])

    return {
        "tooltips_data": dict(tooltips_data),
        "info": _((
            new_born_with_low_weight_help_text(html=True)
        )),
        "chart_data": [
            {
                "values": chart_data['blue'],
                "key": "",
                "strokeWidth": 2,
                "classed": "dashed",
                "color": MapColors.BLUE
            },
        ]
    }
