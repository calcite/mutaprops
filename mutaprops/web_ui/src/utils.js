/**
 * Created by ALCZ11001802 on 2/6/2017.
 */
import _ from 'lodash';

/**
 * Return hashable combination of Object ID and Property ID.
 * Used in the central property storage.
 * @param objId
 * @param propId
 * @returns {string}
 */
function globalPropId (objId, propId) {
    return objId + "-" + propId;
}

/**
 * Check if value is a final value or a dynamic source reference.
 * @param value
 * @returns {*|boolean} True if value is a dynamic source.
 */
function isDynamic (value) {
    // Checks on the signature { type: "source", id: xxx } of source property
    return (_.isPlainObject(value) &&
        _.isEqual(["id", "type"], _.keys(value).sort()) &&
        (["source", "property"].includes(value.type)));
}

/**
 * Parse MutaProp select objects into format usable for Select UI.
 * Three formats are supported: Key-Value dict (JSON), Array of (Key, value)
 * tuples or Array of values.
 * @param selectData
 * @returns {Array}
 */
function parseSelectData (selectData) {
    var selectItems = [];
    if (!selectData) {
        return selectItems;
    }
    if (_.isPlainObject(selectData)) {
        _.forOwn(selectData, (value, key) => {
            selectItems.push({ text: key, value: value})
        });
    } else if (_.isArray(selectData)) {
        if (_.every(selectData, (item) => {
                return (_.isArray(item) && (item.length == 2));
            })) {
            for (let item of selectData) {
                selectItems.push({ text: item[0], value: item[1]})
            }
        } else {
            for (let item of selectData) {
                selectItems.push({ text: item, value: item})
            }
        }
    } else {
        console.error("Invalid select data: " + selectData)
    }
    return selectItems;
}

export {globalPropId, isDynamic, parseSelectData};
