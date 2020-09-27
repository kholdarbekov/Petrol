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

    var csrftoken = Cookies.get('csrftoken');

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
          frm[0].RemainingLitres.value = parseFloat(tbRow.children[1].textContent.replace(',', ''));
          frm[0].bottleVolume.value = parseFloat(tbRow.children[3].textContent.replace(',', ''));
          frm[0].price.value = parseFloat(tbRow.children[5].textContent.replace(',', ''));
          frm[0].RemainingBottles.value = parseInt(tbRow.children[6].textContent.replace(',', ''));
          frm[0].color.value = tbRow.children[7].textContent;
          frm[0].oldName.value = tbRow.children[0].textContent;

          frm[0].action = 'update/';
        });

        $("a:regex(id,^CarBonus)").unbind('click');
        $("a:regex(id,^CarBonus)").on("click",function(e) {
          e.preventDefault(); // cancel the link itself

          var tbRow = this.parentElement.parentElement;

          var result = confirm(tbRow.children[0].textContent + " ga bonus berilmoqda!");
          if(!result){
            return;
          }
          else{
            if (parseInt(tbRow.children[2].textContent.replace(',', '')) < BonusLimit){
              alert("Bu mashina hali bonusga yetmagan")
              return;
            }
          }

          $.ajax({
            url: this.href,
            type: 'post',
            data: {
                carNumber: this.title
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            //dataType: 'json',
            success: function (data) {
                tbRow.children[4].textContent = (parseInt(tbRow.children[4].textContent) + 1).toString();
                tbRow.children[2].textContent = (parseInt(tbRow.children[2].textContent.replace(',', '')) - BonusLimit).toString() + ' L'
                csrftoken = Cookies.get('csrftoken');
            }
          });
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