$(function() {
  'use strict';

  $('#defaultconfig').maxlength({
    warningClass: "badge mt-1 badge-success",
    limitReachedClass: "badge mt-1 badge-danger"
  });

  $('#defaultconfig-2').maxlength({
    alwaysShow: true,
    threshold: 63,
    warningClass: "badge mt-1 badge-success",
    limitReachedClass: "badge mt-1 badge-danger"
  });

  $('#defaultconfig-3').maxlength({
    alwaysShow: true,
    threshold: 10,
    warningClass: "badge mt-1 badge-success",
    limitReachedClass: "badge mt-1 badge-danger",
    separator: ' of ',
    preText: 'You have ',
    postText: ' chars remaining.',
    validate: true
  });

  $('#defaultconfig-4').maxlength({
    alwaysShow: true,
    threshold: 8,
    warningClass: "badge mt-1 badge-success",
    limitReachedClass: "badge mt-1 badge-danger"
  });

  $('#maxlength-textarea').maxlength({
    alwaysShow: true,
    warningClass: "badge mt-1 badge-success",
    limitReachedClass: "badge mt-1 badge-danger"
  });
});