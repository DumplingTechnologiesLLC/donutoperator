

Vue.component('image-row', {
	props: ["imgSrc", "imgId"],
	data: function () {
		return {
			count: 0
		}
	},
	template: `
		
	`
});

var vue_app = new Vue({
    el: '#app',
    delimiters: ["((","))"],
    data: {
    	images: IMAGES,
    },
    methods: {
    	submitNewImage: function() {
    		var self = this;
    		var options = {
		        success: function(data, statusText, xhr, form) {
		        	self.images.push(data)
		        	 $.alert({
	                	title: 'Success',
	                	type: "green",
						content: "Image submitted",
					});
		        	$(window).scrollTop(0);
		        	$("#loader_cover").addClass("toggled");
            		$("#body").removeAttr("style");
		        },
		        error: function(xhr, textStatus, errorThrown) {
			        showErrorMessage('Invalid submission', xhr.responseText);
			        $("#loader_cover").addClass("toggled");
            		$("#body").removeAttr("style");
			    },
		    };
		    $("#body").attr("style", "overflow:hidden");
			$("#loader_cover").removeClass("toggled");
    		$('#image_creation_form').ajaxSubmit(options);
    	},
    	copySrc: function(imgSrc) {
    		/*Copies src to clipboard

    		Expects: 
    		A valid string

    		Arguments:
    		:param imgSrc: a string src of an image

    		Returns:
    		Nothing
    		*/
    		function copyToClp(txt){
			    txt = document.createTextNode(txt);
			    var m = document;
			    var w = window;
			    var b = m.body;
			    b.appendChild(txt);
			    if (b.createTextRange) {
			        var d = b.createTextRange();
			        d.moveToElementText(txt);
			        d.select();
			        m.execCommand('copy');
			    } else {
			        var d = m.createRange();
			        var g = w.getSelection;
			        d.selectNodeContents(txt);
			        g().removeAllRanges();
			        g().addRange(d);
			        m.execCommand('copy');
			        g().removeAllRanges();
			    }
			    txt.remove();
			} 
    		copyToClp(imgSrc);
    	},
    	viewFullImage: function(url){
    		window.open(url)
	    },
    	deleteImage: function(imgId) {
    		var self = this;
    		$.confirm({
                title: 'Are you sure you want to do this?',
                content: "The image will be deleted from the media storage and will stop working in the blog. You'll have to resubmit it and get the new url if you change your mind later.",
                type: 'red',
                typeAnimated: true,
                buttons: {
                    Yes: function(){
                        var data = {
			                csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
			                id: imgId
			            }
			            $(window).scrollTop(0);
			            $("#body").attr("style", "overflow:hidden");
			            $("#loader_cover").removeClass("toggled");
			            $.ajax({
			                type: "POST",
			                url: IMAGE_DELETE_URL,
			                data: data,
			                success: function(data) {
			                   	var index = self.images.findIndex(function(image) {
			                   		if (image.id == imgId) {
			                   			return true;
			                   		}
			                   	});
			                   	self.images.splice(index, 1);
			                   	$("#loader_cover").addClass("toggled");
            					$("#body").removeAttr("style");
			                },
			                error: function(data) {
			                    showErrorMessage('Something happened', data.responseText)
			                    $("#loader_cover").addClass("toggled");
            					$("#body").removeAttr("style");
			                }
			            });
                    },
                    No: function () {

                    }
                }
            });
    	}
    }
})