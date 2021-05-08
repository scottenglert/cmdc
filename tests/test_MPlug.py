"""Test suite for MPlug bindings."""

import nose.tools
import six
import unittest

from maya import cmds 
from maya.api import OpenMaya 

import cmdc

def p(base, *args):
    """Construct a plug string from the given attributes."""

    parts = [base]

    for arg in args:
        if isinstance(arg, (int, float)):
            parts[-1] = '{}[{}]'.format(parts[-1], arg)
        elif isinstance(arg, six.string_types):
            if len(arg) == 1:
                parts[-1] = '{}{}'.format(parts[-1], arg)
            else:
                parts.append(arg)

    return '.'.join(parts)


class TestArrayMethods(unittest.TestCase):
    node = None 

    @classmethod 
    def setUpClass(cls):
        cmds.file(new=True, force=True)

        node = cmds.createNode('network')

        cmds.addAttr(node, ln='array', multi=True)
        cmds.addAttr(node, ln='single', multi=True)
        
        cmds.setAttr(p(node, 'array', 0), 0.0)

        cls.node = node 

    def test_array_pass(self):
        array_element = cmdc.SelectionList().add(p(self.node, 'array', 0)).getPlug(0)
        array_root = array_element.array()

        assert array_root is not None
        assert array_root.name() == p(self.node, 'array')

    def test_array_fail(self):
        array_element = cmdc.SelectionList().add(p(self.node, 'single')).getPlug(0)

        nose.tools.assert_raises(TypeError, array_element.array)
        nose.tools.assert_raises(ValueError, cmdc.Plug().array)


class TestCompoundPlugMethods(unittest.TestCase):
    node = None

    @classmethod 
    def setUpClass(cls):
        cmds.file(new=True, force=True)

        node = cmds.createNode('network')

        cmds.addAttr(node, ln='parent_a', at='compound', nc=1)
        cmds.addAttr(node, ln='child_a', parent='parent_a')

        cmds.addAttr(node, ln='parent_b', at='compound', nc=1)
        cmds.addAttr(node, ln='child_b', parent='parent_b')

        cmds.addAttr(node, ln='single')

        cls.node = node 

    def test_child_pass(self):
        parent = cmdc.SelectionList().add(p(self.node, 'parent_a')).getPlug(0)
        child = cmdc.SelectionList().add(p(self.node, 'parent_a', 'child_a')).getPlug(0).attribute()

        attr = parent.child(child)

        assert attr is not None
        assert attr.name() == p(self.node, 'child_a'), attr.name()

        attr = parent.child(0)
        
        assert attr is not None
        assert attr.name() == p(self.node, 'child_a'), attr.name()

    def test_child_fail(self):
        parent = cmdc.SelectionList().add(p(self.node, 'parent_a')).getPlug(0)
        child = cmdc.SelectionList().add(p(self.node, 'parent_b', 'child_b')).getPlug(0).attribute()

        nose.tools.assert_raises(ValueError, parent.child, child)
        nose.tools.assert_raises(IndexError, parent.child, 1)
        nose.tools.assert_raises(ValueError, cmdc.Plug().child, 0)

    def test_numChildren_pass(self):
        parent = cmdc.SelectionList().add(p(self.node, 'parent_a')).getPlug(0)

        assert parent.numChildren() == 1
        
    def test_numChildren_fail(self):
        non_parent = cmdc.SelectionList().add(p(self.node, 'single')).getPlug(0)

        nose.tools.assert_raises(TypeError, non_parent.numChildren)
        nose.tools.assert_raises(ValueError, cmdc.Plug().numChildren)


class TestConnectionMethods(unittest.TestCase):
    src_node = None 
    tgt_node = None 

    @classmethod 
    def setUpClass(cls):
        src_node = cmds.createNode('network', name='source')
        tgt_node = cmds.createNode('network', name='target')

        cmds.addAttr(src_node, ln='attr', at='double')
        cmds.addAttr(tgt_node, ln='attr', at='doubleAngle')

        cmds.connectAttr(p(src_node, 'attr'), p(tgt_node, 'attr'))

        cls.src_node = src_node
        cls.tgt_node = tgt_node

    def test_source_pass(self):
        src_plug = cmdc.SelectionList().add(p(self.src_node, 'attr')).getPlug(0)
        tgt_plug = cmdc.SelectionList().add(p(self.tgt_node, 'attr')).getPlug(0)

        assert src_plug.source().isNull(), 'Plug.source should return a null plug when not a destination'
        assert tgt_plug.source() == src_plug, 'Plug.source did not return the source plug.'

        nose.tools.assert_raises(ValueError, cmdc.Plug().source)

    def test_sourceWithConversion_pass(self):
        src_plug = cmdc.SelectionList().add(p(self.src_node, 'attr')).getPlug(0)
        tgt_plug = cmdc.SelectionList().add(p(self.tgt_node, 'attr')).getPlug(0)

        assert src_plug.sourceWithConversion().isNull(), 'Plug.sourceWithConversion should return a null plug when not a destination'
        assert tgt_plug.sourceWithConversion() != src_plug, 'Plug.sourceWithConversion skipped over the conversion node'
        assert tgt_plug.sourceWithConversion().node().hasFn(cmdc.Fn.kUnitConversion), 'Plug.sourceWithConversion skipped over conversion node'

        nose.tools.assert_raises(ValueError, cmdc.Plug().sourceWithConversion)
