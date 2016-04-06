require([
    'underscore',
    'backbone',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/tokenutils',
    'splunkjs/mvc/simpleform/formutils',
    'splunkjs/mvc/simpleform/input/timerange',
    'splunkjs/mvc/simpleform/input/submit',
    'splunkjs/mvc/simplexml/element/table',
    'splunkjs/mvc/textinputview',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/searchmanager',
    "splunkjs/mvc/singleview",
    'splunkjs/mvc/simplexml/ready!'
], function(_,
            Backbone,
            $,
            mvc,
            TokenUtils,
            FormUtils,
            TimeRangeInput,
            SubmitButton,
            TableElement,
            TextInputView,
            TableView,
            SearchManager) {

    function resizePanels() {
        var panelRow = $('.dashboard-row').first().next();
        var panelCells = $(panelRow).children('.dashboard-cell');
        $(panelCells[0]).css('width', '30%');
        $(panelCells[1]).css('width', '70%');
        $(window).trigger('resize');
    }

    var typeInput = mvc.Components.get('typeInput');
    var default_tokens = mvc.Components.get("default");
    var tokens = mvc.Components.get("submitted");
    var ipOrDomainInput = mvc.Components.get("ipOrDomainInput");
    var submit = mvc.Components.get("submit");
    var tables = ['pdnsResultsTable', 'sslResultsTable', 'whoisResultsTable', 'pdnsUniqueResultsTable', 'trackerResultsTable', 'accountResultsTable'];
    var searches = ['pdnsQuery', 'sslQuery', 'whoisQuery', 'uniqueQuery', 'enrichmentQuery', 'trackerQuery', 'historyQuery'];
    tokens.set('pt_welcome', 'true');

    ipOrDomainInput.on("change", function(newValue) {
        tokens.unset("pt_query_value");
    });

    var CustomLinkRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            return _(['Resolution', 'IP Address', 'Focus']).contains(cell.field);
        },
        render: function($td, cell) {
            var org_values = cell.value;
            var values = org_values.toString().split(/[, ]+/);
            var td_html = '';
            $.each(values, function(i, value) {
                td_html += '<a class="pivot-link icon-link" href="#"> ' + value + '</a><br/>';
            });
            $td.addClass('pivot-column').html(_.template(td_html));
        }
    });

    $.each(tables, function(i, tableName) {
        var tableEl = mvc.Components.get(tableName);
        tableEl.on('click', function(e) {
            e.preventDefault();
            if($(event.target).attr('class').indexOf("pivot-link") > -1) {
                default_tokens.set('pt_query_value', $(event.target).text());
                ipOrDomainInput.settings.set({ value: default_tokens.get('pt_query_value') });
                FormUtils.submitForm();
            } else {
                FormUtils.submitForm();
            }
        });

        tableEl.getVisualization(function(tableView) {
            tableView.table.addCellRenderer(new CustomLinkRenderer());
            tableView.render();
        });
    });

    $.each(searches, function(i, search) {
        var table = mvc.Components.getInstance(tables[i]);
        var search = mvc.Components.getInstance(search);
        search.on('search:done', function(properties) {
            console.log("Search result", search, properties);
            resizePanels();
            if (search.name != 'historyQuery') {
                tokens.unset('pt_welcome');
            }

            if (search.name == 'sslQuery' && properties.content.resultCount > 0) {
                tokens.set('pt_has_ssl', 'true');
            }

            if (search.name == 'trackerQuery' && properties.content.resultCount > 0) {
                tokens.set('pt_has_trackers', 'true');
            }

            try {
                table.$el.find(".error-response").remove();
            } catch(err) {
                console.log("No errors to remove");
            }

            var responseMsg = properties.content.messages[0];
            if(responseMsg != undefined) {
                var r_type = responseMsg.type;
                var r_text = responseMsg.text;
                if(r_type == 'ERROR') {
                    table.$el.find('.panel-body').append('<div class="error-response">'+r_text+'</div>');
                }
             }
        });
    });
});
