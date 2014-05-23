#!/usr/bin/env python
"""Tests for jss wrapper.
For test to succeed, you need to set up a preferences file at:
~/Library/Preferences/org.da.jss_helper.plist

Create a plist file with the API username and password like so:
defaults write org.da.jss_helper jss_user <username>
defaults write org.da.jss_helper jss_pass <password>
defaults write org.da.jss_helper jss_url <URL to JSS>

"""

import subprocess
import base64
from xml.etree import ElementTree

from nose.tools import *

from jss import *


def std_jss():
    jp = JSSPrefs()
    j = JSS(jss_prefs=jp)
    return j


def setup():
    jp = JSSPrefs()
    global JSSServer
    JSSServer = JSS(jss_prefs=jp)


def test_jssprefs():
    jp = JSSPrefs()
    result = subprocess.check_output(['defaults', 'read', 'org.da.jss_helper', 'jss_user'])
    assert_in(jp.user, result)
    result = subprocess.check_output(['defaults', 'read', 'org.da.jss_helper', 'jss_pass'])
    assert_in(jp.password, result)
    result = subprocess.check_output(['defaults', 'read', 'org.da.jss_helper', 'jss_url'])
    assert_in(jp.url, result)


def test_jssprefs_missing_key_error():
    assert_raises(JSSPrefsMissingKeyError, JSSPrefs, '/nonexistent_path')


def test_jss_with_jss_prefs():
    jp = JSSPrefs()
    j = JSS(jss_prefs=jp)
    assert_is_instance(j, JSS)


def test_jss_with_args():
    authUser = subprocess.check_output(['defaults', 'read', 'org.da.jss_helper', 'jss_user'])
    authPass = subprocess.check_output(['defaults', 'read', 'org.da.jss_helper', 'jss_pass'])
    repoUrl = subprocess.check_output(['defaults', 'read', 'org.da.jss_helper', 'jss_url'])
    j = JSS(url=repoUrl, user=authUser, password=authPass)
    assert_is_instance(j, JSS)


def test_jss_auth_error():
    j = std_jss()
    j.password = 'DonkeyTacos'
    assert_raises(JSSAuthenticationError, j.raw_get, '/policies')


def test_jss_raw_get_error():
    j = std_jss()
    assert_raises(JSSGetError, j.raw_get, '/donkey-tacos')


@with_setup(setup)
def test_jss_put_and_delete():
    with open('doc/policy_template.xml') as f:
        xml = f.read()
    new_policy = JSSServer.Policy(xml)
    # If successful, we'll get a new ID number
    assert_is_instance(new_policy.id(), int)
    id_ = new_policy.id()

    # Test delete
    new_policy.delete()
    assert_raises(JSSGetError, JSSServer.Policy, id_)

#JSSObject Tests###############################################################
def jss_object_runner(object_cls):
    """ Helper function to test individual object classes. Does not test the
    JSS methods for creating these objects.

    """
    j = std_jss()
    obj_list = j.list(object_cls)
    print(obj_list)
    assert_is_instance(obj_list, list)
    # There should be objects in the JSS to test for.
    assert_greater(len(obj_list), 0)
    id_ = obj_list[0].id()
    obj = object_cls(j, id_)
    # This kind_of tests for success, in that it creates an object. The test
    # would fail without the assertion if there was just an exception, but I
    # don't know how to better test this, yet.
    assert_is_instance(obj, object_cls)
    print(type(obj.xml))
    assert_is_instance(obj.xml, ElementTree.Element)
    obj.pprint()


def test_jss_category():
    jss_object_runner(Category)


def test_jss_computer():
    jss_object_runner(Computer)


def test_jss_computergroup():
    jss_object_runner(ComputerGroup)


def test_jss_policy():
    jss_object_runner(Policy)


def test_jss_mobiledevice():
    jss_object_runner(MobileDevice)


def test_jss_mobiledeviceconfigurationprofile():
    jss_object_runner(MobileDeviceConfigurationProfile)


def test_jss_mobiledevicegroups():
    jss_object_runner(MobileDeviceGroup)
