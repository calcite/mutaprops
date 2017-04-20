=======
History
=======

0.5.2 (2017-04-20)
------------------
Fixed bug with Bool-type props help panels not uncollapsing.

0.5.1 (2017-03-06)
------------------
Fixed error message when object was not selected in an one-object list.

0.5.0 (2017-02-15)
------------------
* Large internal rework - introduced update-dependencies for values and
selected meta-values (selects, minimums, maximums, steps etc).
* Added MutaSources as non-UI MutaProps for supporting internal dependencies
* Added HTML type of value (read-only)
* JS client now works with single state-store (Vuex)
* MutaSelects removed - this functionality is now replaced by more general
update-dependencies through MutaSources. This breaks compatibility with 0.4.x

0.4.1 (2016-12-06)
------------------
* Fixed bug with displaying first prop in hierarchy panel.

0.4.0 (2016-12-06)
------------------
* One level hierarchy (panels) and experimental support of toggle buttons instead of checkboxes.

0.3.0 (2016-11-03)
------------------
* Allowed HTML in help blocks
* Allowed local files/local dir

0.2.2 (2016-11-03)
------------------
* Fixed path problem on linux

0.2.1 (2016-11-03)
------------------
* Added ALPS logo

0.2.0 (2016-11-03)
------------------

* HTTP manager chaining.
* UI bugfixes.

0.1.0 (2016-11-03)
------------------

* First (internal) release.
