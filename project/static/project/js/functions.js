/*
 * Template functions file.
 *
 */
jQuery( function() { "use strict";

	var screen_has_mouse = false,
		$window = jQuery( window ),
		$body = jQuery( "body" ),
		$top = jQuery( "#top-header" ),
		$featured = jQuery( "#featured" );

	// Simple way of determining if user is using a mouse device.
	function themeMouseMove() {
		screen_has_mouse = true;
	}
	function themeTouchStart() {
		$window.off( "mousemove.crowdinvest" );
		screen_has_mouse = false;
		setTimeout(function() {
			$window.on( "mousemove.crowdinvest", themeMouseMove );
		}, 250);
	}
	if ( ! navigator.userAgent.match( /(iPad|iPhone|iPod)/g ) ) {
		$window.on( "touchstart.crowdinvest", themeTouchStart ).on( "mousemove.crowdinvest", themeMouseMove );
		if ( window.navigator.msPointerEnabled ) {
			document.addEventListener( "MSPointerDown", themeTouchStart, false );
		}
	}

	if ( window.matchMedia( "(prefers-reduced-motion)" ) ) {
		document.documentElement.className += " reduced-motion";
	}

	// Handle both mouse hover and touch events for traditional menu + mobile hamburger.
	jQuery( "#menu-toggle" ).on( "click.crowdinvest", function( e ) {
		$body.toggleClass( "mobile-menu-opened" );
		e.stopPropagation();
		e.preventDefault();
	});

	jQuery( "#menu-main .current-menu-parent" ).addClass( "collapse" );

	jQuery( document ).on({
		mouseenter: function() {
			if ( screen_has_mouse ) {
				jQuery( this ).addClass( "hover" );
			}
		},
		mouseleave: function() {
			if ( screen_has_mouse ) {
				jQuery( this ).removeClass( "hover" );
			}
		}
	}, ".site-header .menu li" );

	if ( jQuery( "html" ).hasClass( "touchevents" ) ) {
		jQuery( ".site-header .menu .menu-item-has-children > a" ).on( "click.crowdinvest", function (e) {
			if ( ! screen_has_mouse && ! window.navigator.msPointerEnabled && ! jQuery( "#menu-toggle" ).is( ":visible" ) ) {
				var $parent = jQuery( this ).parent();
				if ( ! $parent.parents( ".hover" ).length ) {
					jQuery( ".site-header .menu .menu-item-has-children" ).not( $parent ).removeClass( "hover" );
				}
				$parent.toggleClass( "hover" );
				e.preventDefault();
			}
		});
	} else {
		// Toggle visibility of dropdowns on keyboard focus events.
		jQuery( ".site-header .menu li > a, .site-identity a, .featured-text a, #search-form-input" ).on( "focus.crowdinvest blur.crowdinvest", function(e) {
			if ( screen_has_mouse && ! jQuery( "#menu-toggle" ).is( ":visible" ) ) {
				var $parent = jQuery( this ).parent();
				if ( ! $parent.parents( ".hover" ).length ) {
					jQuery( ".site-header .menu .menu-item-has-children.hover" ).not( $parent ).removeClass( "hover" );
				}
				if ( $parent.hasClass( "menu-item-has-children" ) ) {
					$parent.addClass( "hover" );
				}
				e.preventDefault();
			}
		});
	}

	jQuery( ".site-header .menu .menu-item-has-children > a" ).on( "click.crowdinvest", function (e) {
		if ( jQuery( "#menu-toggle" ).is( ":visible" ) ) {
			jQuery( this ).parent().toggleClass( "collapse" );
			e.preventDefault();
		}
	});

	// Toggle visibility of dropdowns if touched outside the menu area.
	jQuery( document ).on( "click.crowdinvest", function(e) {
		if ( jQuery( e.target ).parents( ".site-header .menu" ).length > 0 ) {
			return;
		}
		jQuery( ".site-header .menu .menu-item-has-children" ).removeClass( "hover" );
	});

	// Handle navigation stickiness.
	if ( $body.hasClass( "navbar-sticky" ) ) {
		var top_nav_height, featured_height;

		var update_sticky_nav_variables = function() {
			top_nav_height  = $top.outerHeight();
			featured_height = $featured.outerHeight() + top_nav_height;
		};

		update_sticky_nav_variables();

		jQuery( window ).on( "resize.crowdinvest", function() {
			if ( window.innerWidth >= 992 ) {
				var isFixed = $body.hasClass( "navbar-is-sticky" );
				$body.removeClass( "navbar-is-sticky" );
				update_sticky_nav_variables();
				if ( isFixed ) {
					$body.addClass( "navbar-is-sticky" );
				}

				// On scroll, we want to stick/unstick the navigation.
				if ( ! $top.hasClass( "navbar-sticky-watching" ) ) {
					$top.addClass( "navbar-sticky-watching" );
					jQuery( window ).on( "scroll.crowdinvest", function() {
						var isFixed = $body.hasClass( "navbar-is-sticky" );
						if ( 1 > ( featured_height - window.pageYOffset ) ) {
							if ( ! isFixed ) {
								$body.addClass( "navbar-is-sticky" );
								if ( parseInt( $featured.css( "margin-top" ), 10 ) != top_nav_height ) {
									$featured.css( "margin-top", top_nav_height );
								}
							}
						} else {
							if ( isFixed ) {
								$body.removeClass( "navbar-is-sticky" );
								$featured.css( "margin-top", "" );
							}
						}
					} ).scroll();
				}
			} else {
				if ( $top.hasClass( "navbar-sticky-watching" ) ) {
					$top.removeClass( "navbar-sticky-watching" );
					jQuery( window ).unbind( "scroll.crowdinvest" );
					$body.removeClass( "navbar-is-sticky" );
					$featured.css( "margin-top", "" );
				}
			}
		}).resize();
	}

	// Handle tab navigation with hash links.
	jQuery( ".tabs a" ).on( "click.crowdinvest", function (e) {
		if ( jQuery( this ).hasClass( "tab-link-active" ) ) {
			e.preventDefault();
			return;
		}
		var $target = jQuery( jQuery( this ).attr( "href" ) );
		$target.attr( "data-id", $target.attr( "id" ) ).attr( "id", "" );
	});

	jQuery( window ).on( "hashchange", function() {
		if ( ! window.location.hash ) {
			return;
		}
		var $active_tab_content = jQuery( '.tab-content[data-id="' + window.location.hash.substring( 1 ) + '"]' );
		if ( $active_tab_content.length == 0 ) {
			return;
		}
		$active_tab_content.attr( "id", $active_tab_content.data( "id" ) );
		var $tab_container = $active_tab_content.parent();
		$tab_container.find( ".tab-content:not(#" + $active_tab_content.data( "id" ) + ")" ).removeClass( "tab-active" );
		$active_tab_content.addClass( "tab-active" );
		$tab_container.find( ".tabs a" ).removeClass( "tab-link-active" ).filter( '[href="' + window.location.hash + '"]' ).addClass( "tab-link-active" );
	});

	if ( window.location.hash ) {
		var $active_tab = jQuery( '.tabs a[href="' + window.location.hash + '"]' );
		if ( $active_tab.length > 0 ) {
			$active_tab.trigger( "click" );
			jQuery( window ).trigger( "hashchange" );
		}
	}
	jQuery( ".tab-container" ).addClass( "tabs-loaded" );

	if ( jQuery.fancybox ) {
		jQuery.fancybox.defaults.hideScrollbar = false;
		jQuery.fancybox.defaults.backFocus     = false;
		jQuery.fancybox.defaults.padding       = 0;

		jQuery( ".gallery" ).each( function() {
			var gallery_id = jQuery( this ).attr( "id" );
			jQuery( this ).find( ".gallery-item" ).each( function() {
				var gallery_item_caption = jQuery( ".gallery-caption", this ).text().trim(), $gallery_item_link = jQuery( ".gallery-icon a", this );
				if ( $gallery_item_link.attr( "href" ) && $gallery_item_link.attr( "href" ).match(/\.(jpeg|jpg|gif|png)$/) !== null ) {
					$gallery_item_link.attr( "data-fancybox", gallery_id ).attr( "data-caption", gallery_item_caption );
				}
			});
		});
		jQuery( ".wp-caption a, .single-attachment .attachment a" ).has( "img" ).attr( "data-fancybox", "" );
	}

	// Handle career position collapsable items.
	jQuery( ".career-position .toggle-details" ).on( "click.crowdinvest", function (e) {
		e.preventDefault();
		var $wrapper = jQuery( this ).parents( ".career-position" );
		$wrapper.toggleClass( "opened" );
	});

	// Handle career position collapsable items.
	jQuery( ".helpfulness-rating .rating-form a" ).on( "click.crowdinvest", function (e) {
		e.preventDefault();
		jQuery( this ).parents( ".helpfulness-rating" ).addClass( "feedback-received" );
	});

	// Handle chat window (example of functionality).
	jQuery( ".video-wrapper .video-playback" ).on( "click.crowdinvest", function (e) {
		var media_id = jQuery( this ).attr( "href" ), media = document.getElementById( media_id.substring(1) ), $wrapper = jQuery( this ).parent();
		media.wrapper = $wrapper;
		if ( media.paused ) {
			media.play();
		} else {
			media.pause();
		}
		if ( ! $wrapper.hasClass( "init-events" ) ) {
			jQuery( media_id ).on( "play", function( e ) {
				this.wrapper.removeClass( "status-pause" ).addClass( "status-play" ).find( ".video-playback em:first-child" ).removeClass( "mdi-replay" ).addClass( "mdi-play" );
			}).on( "pause", function() {
				this.wrapper.removeClass( "status-play" ).addClass( "status-pause" );
			}).on( "timeupdate", function() {
				this.wrapper.find( ".video-playback .progress" ).css( "width", ( this.currentTime / this.duration * 100 ) + "%" );
			}).on( "ended", function() {
				this.wrapper.removeClass( "status-play" ).addClass( "status-pause" ).find( ".video-playback em:first-child" ).removeClass( "mdi-play" ).addClass( "mdi-replay" );this.wrapper.find( ".video-playback .progress" ).removeAttr( "style" );
			});
			$wrapper.addClass( "init-events" );
		}
		e.preventDefault();
	});

	// Handle statistics animation.
	jQuery( '.statistics.style-horizontal' ).each( function() {
		jQuery( '.statistics-item', this ).each( function( i ) {
			var $bar = jQuery( this );
			setTimeout( function() {
				$bar.css( "width", $bar.attr( "data-percent") );
				}, i * 20);
		});
	});
	jQuery( '.statistics.style-vertical' ).each( function() {
		jQuery( '.statistics-item', this ).each( function( i ) {
			var $bar = jQuery( this );
			setTimeout( function() {
				$bar.css( "height", $bar.attr( "data-percent") );
				}, i * 20);
		});
	});

	// Scroll top top functionality.
	var $goToTopLink = jQuery( ".to-the-top" ).on( "click.crowdinvest", function( e ) {
		if ( $body.hasClass( "reduced-motion" ) ) {
			window.scrollTo(0, 0);
		} else {
			jQuery( "html, body" ).animate( {
				scrollTop: 0
			}, {
				duration: 800,
				easing: "swing"
			} );
		}
		e.stopPropagation();
		e.preventDefault();
	});


	// Toggle go-to-top visibility and avoid using any event on mobile devices (for better performance).
	if ( $goToTopLink.length > 0 ) {
		var goToTopLimit = $top.outerHeight() + $featured.outerHeight();
		jQuery( window ).on( "resize.to-top-crowdinvest", function() {
			if ( window.innerWidth >= 768 ) {
				goToTopLimit = $top.outerHeight() + $featured.outerHeight();
				if ( ! $goToTopLink.hasClass( "watching" ) ) {
					$goToTopLink.addClass( "watching" );
					jQuery( window ).on( "scroll.to-top-crowdinvest", function() {
						$goToTopLink.toggleClass( "active", jQuery( window ).scrollTop() > goToTopLimit );
					} );
				}
			} else {
				if ( $goToTopLink.hasClass( "watching" ) ) {
					$goToTopLink.removeClass( "watching" );
					jQuery( window ).unbind( "scroll.to-top-crowdinvest" );
				}
			}
		}).resize();
	}


	// Handle chat window (example of functionality).
	jQuery( ".support-chat .chat-toggle" ).on( "click.crowdinvest", function (e) {
		jQuery( ".support-chat" ).toggleClass( "chat-opened" );
		if ( jQuery( ".support-chat" ).hasClass( "chat-opened" ) ) {
			jQuery( ".support-chat .badge" ).remove();
			window.setTimeout(function() {
				jQuery( ".support-chat .input-message" ).focus();
			}, 50);
		}
		e.stopPropagation();
		e.preventDefault();
	});
	jQuery( ".support-chat .input-message" ).on( "keypress.crowdinvest", function (e) {
		var keycode = ( e.keyCode ? e.keyCode : e.which );
		if ( "13" == keycode && "" != jQuery( this ).val() ) {
			jQuery( ".support-chat .chat-messages .message:last-child" ).after( '<p class="message message-user">' + jQuery( this ).val() + '</p>' ).val( "" );
			jQuery( ".support-chat .chat-messages" ).scrollTop( jQuery( ".support-chat .chat-messages" ).prop( "scrollHeight" ) );
			// post message via AJAX
			jQuery( this ).val( "" );
		}
		e.stopPropagation();
	});

});
