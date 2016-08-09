$(function(){
	$('.datepicker').datepicker({ 
		dateFormat: 'yy-mm-dd', 
		maxDate: '+0d'
	});

	function checkDate(datestr) {
		if(!datestr.match(/^\d{4}\-\d{2}\-\d{2}$/)){
			return false;
		}

		var vYear = datestr.substr(0, 4);
		var vMonth = datestr.substr(5, 2) - 1;
		var vDay = datestr.substr(8, 2);

		if(vMonth >= 0 && vMonth <= 11 && vDay >= 1 && vDay <= 31) {
			var vDt = new Date(vYear, vMonth, vDay);
			if(isNaN(vDt)) {
				return false;
			} else if(vDt.getFullYear() == vYear && vDt.getMonth() == vMonth && vDt.getDate() == vDay) {　　
				return true;
			} else {
				return false;
			}
		} else {
			return false;
		}
	}

	function convertDate(datestr) {
		var vYear = datestr.substr(0, 4);
		var vMonth = datestr.substr(5, 2) - 1;
		var vDay = datestr.substr(8, 2);
		return new Date(vYear, vMonth, vDay);
	}

	$('#l-btn').click(function() {
		var isBlank = false;
		$('.error').remove();
		$('input,label,select').removeClass('ipt-error  errorBox');

		if ($('#s-validate').val() == "0") {
			$('#s-validate').addClass('ipt-error');
			$('#s-validate').parent().append('<p class="error">選択してください</p>');
		}

		$('.datepicker').each(function() {
			if ((!$(this).val()) || (!checkDate($(this).val()))) {
				$(this).addClass('ipt-error errorBox');
				$(this).parent().append('<p class="error">入力してください</p>');
				isBlank = true;
			}
		});

		if(!isBlank) {
			var startDate = convertDate($('#startDate').val()).getTime();
			var endDate = convertDate($('#endDate').val()).getTime();
			if (startDate > endDate) {
				$('#endDate').addClass('ipt-error errorBox');
				$('#endDate').parent().append('<p class="error">終了日は開始日以降の日付を指定してください</p>');
			}
		}

		if ($('#rowLimit').val() && $('#rowLimit').val().match(/[^0-9]+/)) {
			$('#rowLimit').addClass('ipt-error errorBox');
			$('#rowLimit').parent().append('<p class="error">半角数字で入力してください</p>');
		}

		var Size = $('.ipt-error').size();
		if (Size > 0) {
			$('body,html').animate({ scrollTop: $('.error:first').offset().top-80 }, 600);
			return false;
		}
	});
});