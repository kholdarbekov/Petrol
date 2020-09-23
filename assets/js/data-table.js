$(function() {
  'use strict';

  $(function() {
    jQuery.expr[':'].regex = function(elem, index, match) {
        var matchParams = match[3].split(','),
        validLabels = /^(data|css):/,
        attr = {
            method: matchParams[0].match(validLabels) ?
                        matchParams[0].split(':')[0] : 'attr',
            property: matchParams.shift().replace(validLabels,'')
        },
        regexFlags = 'ig',
        regex = new RegExp(matchParams.join('').replace(/^\s+|\s+$/g,''), regexFlags);
        return regex.test(jQuery(elem)[attr.method](attr.property));
        }

    const csrftoken = Cookies.get('csrftoken');

    var dataTableExample = $('#dataTableExample').DataTable({
      "aLengthMenu": [
        [10, 30, 50, -1],
        [10, 30, 50, "All"]
      ],
      "iDisplayLength": 10,
      "language": {
        search: ""
      },
      "fnDrawCallback": function( oSettings ) {
        $("a:regex(id,^Delete)").unbind('click');
        $("a:regex(id,^Delete)").on("click",function(e) {
          e.preventDefault(); // cancel the link itself
          var result = confirm("Are you sure to delete?");
          if(!result){
            return;
          }
          var tbRow = this.parentElement.parentElement;

          $.ajax({
            url: this.href,
            type: 'post',
            data: {
                pk: this.title
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            //dataType: 'json',
            success: function (data) {
                dataTableExample.row(tbRow).remove().draw();
            }
          });
        });

        $("a:regex(id,^Change)").unbind('click');
        $("a:regex(id,^Change)").on("click",function(e) {
          e.preventDefault(); // cancel the link itself
          var tbRow = this.parentElement.parentElement;
          var frm = $('#signupForm');

          frm[0].name.value = tbRow.children[0].textContent;
          frm[0].RemainingLitres.value = parseInt(tbRow.children[1].textContent);
          frm[0].bottleVolume.value = parseInt(tbRow.children[3].textContent);
          frm[0].price.value = parseFloat(tbRow.children[5].textContent.replace(',', ''));
          frm[0].RemainingBottles.value = tbRow.children[6].textContent;
          frm[0].color.value = tbRow.children[7].textContent;

          frm[0].action = 'update/';
        });
      }
    });

    $('#dataTableExample').each(function() {
      var datatable = $(this);
      // SEARCH - Add the placeholder for Search and Turn this into in-line form control
      var search_input = datatable.closest('.dataTables_wrapper').find('div[id$=_filter] input');
      search_input.attr('placeholder', 'Search');
      search_input.removeClass('form-control-sm');
      // LENGTH - Inline-Form control
      var length_sel = datatable.closest('.dataTables_wrapper').find('div[id$=_length] select');
      length_sel.removeClass('form-control-sm');
    });

  });
});