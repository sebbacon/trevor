$(document).ready(function() {
	$(".clear-on-click").resetDefaultValue()
	$('a.show-prediction').click(function() {
		$('div.prediction').css('display', 'none');
		$(this).next('div.prediction').css('display','block');
		return false;
	    });
	$('a#nonfacebooklogin').click(function(){
		$('.nonfacebook').toggle();
		$('.facebook').toggle();		
		    });
	$('a#nonfacebookregister').click(function(){
		$('.nonfacebookregister').toggle();
		$('.facebookregister').toggle();		
		    });
	$("#prediction").sortable({ 
		    handle : '.handle',
		    containment: $('.prediction-panel'),
		    opacity: 0.7,
		    scroll: true
	    }); 
	$("#loginlink").click(function() {
		var form = $('#loginform');
		var mainpos = $('#main').position();
		var top = mainpos.top;
		var left = mainpos.left + $('#main').width() - form.width();
		form.css({top:mainpos.top, left: left});
		form.css('display','block');
		return false;
	    });

	$("body").click(function() {
		var form = $('#loginform');
		form.css('display','none');
		$('div.prediction').css('display', 'none');
	    });
	$("#loginform").click(function(event){
		event.stopPropagation();
	    });
	//$("div.prediction").click(function(event){
	//	event.stopPropagation();
	//    });
	$("div.row").equalHeights();
	$("tr.field_email:not(tr.errors) td:gt(3)").parent().addClass('hidden-row');
	$("#add-email").click(function(){
		var foo = $('tr.hidden-row:first');
		foo.removeClass('hidden-row');
		   
	    });
	var teams_select = $('#id_supported_team').clone();
	
	$("#team_division").change(function(){
		var division = 'division-' + $(this).attr('value');
		var new_select = teams_select.clone().children().remove().end();
		var teams = teams_select.children();
		teams.each(function(i) {
			var team = $(this);
			if ($(team).attr('class') == division) {
			    new_select.append(team);
			}
		    });
		$('#id_supported_team').html($(new_select).html());
	    });

	$('#id_supported_team options::first').select();

	var pos = $('#personal-selection').position();
	if (pos) {
	    $('#current-actual-table').css({top:pos.top, left:pos.left}).width($('#personal-selection').width());
	}
	$('#show-current').click(function() {
                //$('#personal-selection').fadeOut();
		$('#current-actual-table').fadeIn();
		$('#personal-selection').prev().text("Current table")
	    });
	$('#show-selection').click(function() {
		$('#current-actual-table').fadeOut();
                $('#personal-selection').fadeIn();
		$('#personal-selection').prev().text("My selection")
	    });
	$('#tabs').tabs();
	$('a.button').button();
    });


/**
 * jQuery resetDefaultValue plugin
 * @version 0.9.1
 * @author Leandro Vieira Pinho 
 */
jQuery.fn.resetDefaultValue = function() {
	function _clearDefaultValue() {
		var _$ = $(this);
		if ( _$.val() == this.defaultValue ) { _$.val(''); }
	};
	function _resetDefaultValue() {
		var _$ = $(this);
		if ( _$.val() == '' ) { _$.val(this.defaultValue); }
	};
	return this.click(_clearDefaultValue).focus(_clearDefaultValue).blur(_resetDefaultValue);
}

$.fn.equalHeights = function(px) {
$(this).each(function(){
var currentTallest = 0;
$(this).children().each(function(i){
    if ($(this).height() > currentTallest) { currentTallest = $(this).height(); }
        });
    currentTallest = currentTallest + "px"; //use ems unless px is specified
        // for ie6, set height since min-height isn't supported
    if ($.browser.msie && $.browser.version == 6.0) { $(this).children().css({'height': currentTallest}); }
        $(this).children().css({'min-height': currentTallest}); 
    });
    return this;
};
