=== Simple Section Navigation Widget ===
Contributors: jakemgold, thinkoomph
Donate link: http://www.get10up.com/plugins/simple-section-navigation/
Tags: navigation, section, cms, pages, top level, hierarchy
Requires at least: 2.8
Tested up to: 3.1
Stable tag: 2.1

Adds a widget for section (or top level page) based page navigation. Essential for CMS! Includes simple function for template developers.

== Description ==

Adds a widget to your sidebar for section based navigation. Essential for CMS implementations! 

The title of the widget is the top level page within the current section. Shows all page siblings (except on the top level page), all parents and grandparents (and higher), the siblings of all parents and grandparents (up to top level page), and any immediate children of the current page. Can also be called by a function inside template files.

It includes a simple widget configuration panel. From this panel you can:

1. Determine whether the widget should appear on the home page
1. Override standard behavior and have the widget show all pages in the current section
1. Determine whether the widget should appear even if the section only has one page (the top level)
1. Provide a list of pages to exclude from the output
1. Determine whether the section navigation should still appear when viewing excluded pages
1. Use a specific widget title (i.e. In This Section), or just use the top level page title
1. Determine whether the section title should be linked
1. Determine page sort order (defaults to menu order)

The widget uses standard WordPress navigation classes, in addition to a unique class around the widget, for easy styling.

ATTENTION UPGRADERS: version 2.0 represents a fundamental change to the plug-in's architecture. Version 2 will attempt to seamlessly upgrade the old the widget, but you should document your current settings before pgrading. If you are calling it by a function in the template (not using the widget), you will be required to update your template, unless you were using the default settings. The function now has 1 parameter: arguments for the output of the widget, as detailed under installation instructions.

Compatible with WordPress MU.


== Installation ==

1. Install easily with the WordPress plugin control panel or manually download the plugin and upload the extracted
folder to the `/wp-content/plugins/` directory
1. Activate the plugin through the 'Plugins' menu in WordPress
1. Widget users can add it to the sidebar by going to the "Widgets" menu under "Appearance" and adding the "Simple
Section Navigation" widget. Open the widget to configure.
1. Template authors can call the navigation by using the `simple_section_nav` function. The function accepts a single
argument in the form of a classical WordPress set of parameters.

= Parameters =

* `show_all` - Always show all pages in current section (default: false)
* `exclude` - Page IDs, seperated by commas, of pages to exclude (default: '')
* `hide_on_excluded` - No navigation on excluded pages (default: true)
* `show_on_home` - Show top level page list on home page (default: false)
* `show_empty` - Output even if empty section (default: false)
* `sort_by` - Page sort order; can use any WordPress page list sort value (default: menu_order)
* `title` - Provide a specific widget title; default is the top level page title (default: '')
* `a_heading` - Show all pages in section (default: false)
* `before_widget` - HTML before widget (default: `<div>`)
* `after_widget` - HTML after widget (default: `</div>`)
* `before_title` - HTML before widget (default: `<h2 class="widgettitle">`)
* `after_title` - HTML after widget (default: `</h2>`)

= Example =

`simple_section_nav('before_widget=<li>&after_widget=</li>&exclude=2&show_on_home=1');`

Will wrap the widget in LI tags, exclude page ID 2, and will output on home page.


== Screenshots ==

1. Screenshot of widget output on "Open Source" page under top level page "My Portfolio", running Twenty-Ten theme
2. Screenshot of widget configuration.


== Changelog ==

= 2.1 =
* Ability to specify the widget title (still defaults to top level page name)
* New filter for widget title, `simple_section_nav_title`, for greater developer control over title
* Various minor optimizations for performance, widget option sanitizing, best coding practices

= 2.0.2 =
* Applies `simple_section_page_list` filter to child page list before output
* Adds "current_page_parent" class to linked heading, if applicable
* Improved logic around page ancestors in the excluded list
* Fixes rare error involving post ancestor setup
* Many general improvement and optimizations to codebase

= 2.0.1 =
* Ability to customize "before_title" and "after_title" when calling via template function

= 2.0 =
Version 2.0 represents a fundamental change to the plug-in's architecture. Developers calling the widget by a function in the template (not using the widget) will be *required* to update the template, unless using the default settings. The function now has 1 parameter: arguments for the output of the widget, as detailed under installation instructions. New features include multiwidget support, better performance, and independent configuration for each instance.

= 1.3.1 =
* Fixes and optimizes output on posts page, posts, and archives

= 1.3 =
* Ability to set page sort order (still defaults to menu order)
* Applies current_page_item and current_page_ancestor classes to optional heading link
* Easy access to settings panel from plug-ins page
* WordPress 2.8 compatibility check

= 1.2 =
* DEFINITIVE FIX FOR PAGE FLATTENING / FLAT HIERARCHY / NO DEPTH ISSUES
* Performance improvements

= 1.1.2 =
* Fixed occassional flattening or wrong order of hierarchical pages

= 1.1 =
* Added ability to link heading, which also wraps it in a unique id
* Improved excluded pages handling
* Ability to exclude entire sections from using the widget

= Future features =
* Lists private pages if user has permission to see them
* Ability to set a maximum page depth for display in widget


== Upgrade Notice ==

= 2.0 =
2.0 is a major update to the plug-in internals. The update will attempt to keep all settings. Document your settings to be safe. If you are calling simple_section_nav in the template code you *must* update your code (unless using default settings). See installation instructions for details.