# -*- coding: utf-8 -*-
'''
Created on 2014-2-10

'''
from __future__ import absolute_import
from __future__ import unicode_literals
from flask import Blueprint, flash, render_template
from flask.globals import current_app
from flask.helpers import make_response, url_for
import os
import pygal
from pygal.style import Style
from datetime import datetime
from ...common.const import DASHBOARD_NODE
from ...common.model_meta import dashboard_pagelet, dashboard_page
from ...common.model_meta import Summary, CheckItemStatistics
from ...common.model_meta import dashboard_check_cfg, team_mail_cfg


mod = Blueprint('dashboard', __name__)  # register the users blueprint module


class PageletComponent(object):

    '''
    one object combine pagelet basic info and check list objects
    '''

    def __init__(self, pagelet_code):
        self.pagelet_code = pagelet_code
        self.pagelet_entity = dashboard_pagelet.getOnePagelet(pagelet_code)
        self.pagelet_title = self.pagelet_entity.pagelet_title
        self.check_list = self.pagelet_entity.getCheckItems()


@mod.route("/")
@mod.route("/pages")
def index():
    visible_pages = dashboard_page.getAllPages()
    summary_list = Summary.get_all_pages_summary()
    return render_template("index.html",
                           root=DASHBOARD_NODE,
                           current_page_code=DASHBOARD_NODE,
                           pages=visible_pages,
                           page_summary_list=summary_list,
                           refresh_timestamp=datetime.now().strftime("%H:%M:%S")
                           )


@mod.route("/pages/<page_code>")
def page_view(page_code):
    pages = dashboard_page.getAllPages(including_hiden=True)
    if not [p for p in pages if p.page_code == page_code]:
        flash('There is no page with code as "%s", please use side bar to navigate.' % (page_code), category="info")
    visible_pages = dashboard_page.getAllPages()

    pagelets = dashboard_pagelet.getAllPagelets(page_code)
    pagelet_summary_list = Summary.get_all_pagelets_summmary(page_code)
    pagelet_components = [PageletComponent(pl.pagelet_code) for pl in pagelets]

    return render_template("page.html",
                           root=DASHBOARD_NODE,
                           current_page_code=page_code,
                           pages=visible_pages,
                           pagelet_summary_list=pagelet_summary_list,
                           pagelet_components=pagelet_components,
                           refresh_timestamp=datetime.now().strftime("%H:%M:%S")
                           )


def getDatesInShortFormat(date_list):
    # return date_list
    return [date[4:6] + '-' + date[6:] for date in date_list]


def getKeyDates(date_list):
    return filter(lambda d: d[6:] in ['01', '05', '10', '15', '20', '25'], date_list)


def initStatusChart(check_item, isShortTerm=True):
    statistics = CheckItemStatistics(check_item)
    if isShortTerm:
        data = statistics.getShortTermStatusData()
        # data elements: [date_list, normal_list, warning_list, critical_list, term_month_count]
        term_month_count = data[4]
        title = 'Status statistics in short term(%d months)' % (term_month_count)

    else:
        data = statistics.getLongTermStatusData()
        # data elements: [date_list, normal_list, warning_list, critical_list, term_month_count]
        term_month_count = data[4]
        title = 'Status statistics in long term(%d months)' % (term_month_count)

    date_list = data[0]
    date_list_short_format = getDatesInShortFormat(date_list)
    key_date_list_short_format = getDatesInShortFormat(getKeyDates(date_list))
    normal_list = data[1]
    warning_list = data[2]
    critical_list = data[3]

    custom_style = Style(colors=(
        '#b6e354'  # green
        , '#fd971f'  # yellow
        , '#DC3912'  # red
        ))
    chart = pygal.Line(style=custom_style, legend_at_bottom=True, legend_box_size=18)
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    chart.js = [os.path.join(SITE_ROOT, "static/js/", "svg.jquery.js"),
                os.path.join(SITE_ROOT, "static/js/", "pygal-tooltips.js")]
    if isShortTerm:
        chart.height = 420
        chart.width = 900
    else:
        chart.height = 420
        chart.width = 2000
    chart.disable_xml_declaration = True  # disable xml root node
    chart.x_label_rotation = 30
    chart.title = title
    chart.x_title = 'Timeline'
    chart.y_title = 'Status count'

    chart.x_labels = map(str, date_list_short_format)
    chart.x_labels_major = key_date_list_short_format
    chart.add('Normal count', normal_list)
    chart.add('Warning count', warning_list)
    chart.add('Critical count', critical_list)

    return chart


def initValueChart(check_item, isShortTerm=True):
    statistics = CheckItemStatistics(check_item)
    if isShortTerm:
        data = statistics.getShortTermValueData()
        term_month_count = data[6]
        # data elements: [date_list, avg_value_list, min_value_list, max_value_list, warning_limit_list, critical_limit_list, term_month_count]
        title = 'Value statistics in short term(%d months)' % (term_month_count)
    else:
        data = statistics.getLongTermValueData()
        # data elements: [date_list, avg_value_list, min_value_list, max_value_list, warning_limit_list, critical_limit_list, term_month_count]
        term_month_count = data[6]
        title = 'Value statistics in long term(%d months)' % (term_month_count)

    date_list = data[0]
    date_list_short_format = getDatesInShortFormat(date_list)
    key_date_list_short_format = getDatesInShortFormat(getKeyDates(date_list))
    avg_value_list = data[1]
    min_value_list = data[2]
    max_value_list = data[3]
    warning_limit_list = data[4]
    critical_limit_list = data[5]

    custom_style = Style(colors=(
        '#fd971f'  # yellow--warning
        , '#DC3912'  # red--critical
        , '#6c71c4'  # min
        , '#8000FF'  # max
        , '#00FFFF'  # avg
        ))
    chart = pygal.Line(style=custom_style, legend_at_bottom=True, legend_box_size=18)
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    chart.js = [os.path.join(SITE_ROOT, "static/js/", "svg.jquery.js"),
                os.path.join(SITE_ROOT, "static/js/", "pygal-tooltips.js")]
    if isShortTerm:
        chart.height = 420
        chart.width = 900
    else:
        chart.height = 700
        chart.width = 2000
    chart.disable_xml_declaration = True  # disable xml root node
    chart.x_label_rotation = 30
    chart.title = title
    chart.x_title = 'Timeline'
    chart.y_title = 'Value'

    chart.x_labels = map(str, date_list_short_format)
    chart.x_labels_major = key_date_list_short_format
    chart.add('Warning limit', warning_limit_list)
    chart.add('Critical limit', critical_limit_list)
    chart.add('Min value', min_value_list)
    chart.add('Max value', max_value_list)
    chart.add('Avg value', avg_value_list)

    return chart


# http://127.0.0.1:5000/items/UNIT_TEST_NONNUMERICAL
# http://127.0.0.1:5000/items/UNIT_TEST_NUMERICAL
@mod.route("/items/<itm_code>")
def item_view(itm_code):
    all_check_items = dashboard_check_cfg.getAllChkItems()
    if not [c for c in all_check_items if c.itm_code == itm_code]:
        flash('There is no checking item with code as "%s", pls check.' % (itm_code), category="info")
        check_item = None
    else:
        check_item = [c for c in all_check_items if c.itm_code == itm_code][0]

    svg_status_stat_short = None
    svg_status_stat_long = None

    if check_item:
        chart = initStatusChart(check_item, isShortTerm=True)
        svg_status_stat_short = chart.render()
        chart = initStatusChart(check_item, isShortTerm=False)
        svg_status_stat_long = chart.render()
        svg_status_stat_long = '<svg  style="width:2100px" ' + svg_status_stat_long[4:]  # set canvas size

    svg_value_stat_short = None
    svg_value_stat_long = None
    owner_teams = []
    if check_item:
        owner_teams = check_item.owner_team_list.replace(',', ';').split(';')
        owner_teams = [team.strip() for team in owner_teams]

        if check_item.check_value_is_number == 'Y':
            chart = initValueChart(check_item, isShortTerm=True)
            svg_value_stat_short = chart.render()

            chart = initValueChart(check_item, isShortTerm=False)
            svg_value_stat_long = chart.render()
            svg_value_stat_long = '<svg  style="width:2100px" ' + svg_value_stat_long[4:]  # set canvas size

    return render_template("check_item.html",
                           check_item=check_item,
                           owner_teams=owner_teams,
                           svg_status_stat_short=svg_status_stat_short,
                           svg_status_stat_long=svg_status_stat_long,
                           svg_value_stat_short=svg_value_stat_short,
                           svg_value_stat_long=svg_value_stat_long,
                           )


@mod.route("/teams/<team_code>")
def team_view(team_code):
    team = team_mail_cfg.getCfgInDb(team_code)
    if team is None:
        flash('There is no team with code as "%s".' % (team_code), category="info")
    else:
        return render_template("team.html",
                               team=team,
                               )


@mod.route("/svg")
def raw_svgs():
    chart = pygal.Line(legend_at_bottom=True, legend_box_size=18)

    # =======================================
    # Declare the location of svg.jquery.js and pygal-tooltips.js in server side.
    # =======================================
    # It must be declare in server side, not html file
    # if not declare in server, by default it will load the two js files located in http://kozea.github.com/pygal.js. And it will slow down the page loading

    # 1, It works, load local js files
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    chart.js = [os.path.join(SITE_ROOT, "static/js/", "svg.jquery.js"),
                os.path.join(SITE_ROOT, "static/js/", "pygal-tooltips.js")]

    # 2.a, It Works, but it is ugly because it use local absolute http url
    # chart.js =['http://127.0.0.1:5000/static/js/svg.jquery.js',
    #     'http://127.0.0.1:5000/static/js/pygal-tooltips.js']

    # 2.b, works, use local CDN absolute http url
    # chart.js =['http://another_server/pygal-tooltips.js',
    #     'http://another_server/svg.jquery.js']

    # 3, Does not work, error raised at visiting, IOError: [Errno 2] No such file
    # chart.js = [url_for('static', filename='js/svg.jquery.js'),
    #            url_for('static', filename='js/pygal-tooltips.js')]

    # disable xml root node
    chart.disable_xml_declaration = True
    chart.title = 'Browser usage evolution (in %)'
    chart.width = 2000
    chart.height = 2000
    chart.x_labels = map(str, range(2002, 2013))
    chart.add('Firefox', [None, None, 0, 16.6, 25, 31, 36.4, 45.5, 46.3, 42.8, 37.1])
    chart.add('Chrome', [None, None, None, None, None, None, 0, 3.9, 10.8, 23.8, 35.3])
    chart.add('IE', [85.8, 84.6, 84.7, 74.5, 66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    chart.add('Others', [14.2, 15.4, 15.3, 8.9, 9, 10.4, 8.9, 5.8, 6.7, 6.8, 7.5])

    svg_xml = chart.render()
    svg_xml = '<svg  style="width:2000px" ' + svg_xml[4:]
    svg_xml1 = svg_xml[:100]
    response = make_response(render_template('test_svg.html', title=svg_xml1, svg_xml=svg_xml))
    # response.headers['Content-Type']='image/svg+xml' 不能设置Content-Type为svg模式
    return response
