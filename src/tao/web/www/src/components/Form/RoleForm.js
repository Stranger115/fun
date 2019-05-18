'use strict'

import React from 'react'
import {Form, Input, Button, message, Select} from 'antd'
import { FormItemLayout, FormItemLayoutWithOutLabel } from "../../constants"
import axios from "axios";


const { TextArea } = Input;
const Option = Select.Option
const FormItem = Form.Item

export const EditableContext = React.createContext()

const EditableRow = ({ form, index, ...props }) => (
  <EditableContext.Provider value={form}>
    <tr {...props} />
  </EditableContext.Provider>
)


export const EditableFormRow = Form.create()(EditableRow)

export class EditableCell extends React.Component {
  constructor(props) {
    super(props)
    this.role = null
    }
  getInput = () => {
    const dataIndex = this.props.dataIndex
    if  (dataIndex === 'permission' ){
      return <Select
              mode="multiple"
              placeholder="请选择权限"
              >
                <Option key={0x01} value={0x01}>商品购买</Option>
                <Option key={0x02} value={0x02}>账单管理</Option>
                <Option key={0x04} value={0x04}>会员管理</Option>
                <Option key={0x08} value={0x08}>权限管理</Option>
                <Option key={0x10} value={0x10}>商品管理</Option>
              </Select>
    }

    return <Input style={{ width: '70%' }} />
  }
  render() {
    const {
      editing,
      dataIndex,
      title,
      inputType,
      record,
      index,
      ...restProps
    } = this.props
    return (
      <EditableContext.Consumer>
        {(form) => {
          const { getFieldDecorator } = form
          return (
            <td {...restProps}>
              {(editing && record['level']!==0)? (
                <FormItem style={{ margin: 0 }}>
                  {getFieldDecorator(dataIndex, {
                    rules: [{
                      required: true,
                      message: `请输入 ${title}!`,
                    }],
                    initialValue: record[dataIndex],
                  })(this.getInput())}
                </FormItem>
              ) : restProps.children}
            </td>
          )
        }}
      </EditableContext.Consumer>
    )
  }
}

function hasErrors(fieldsError) {
  return Object.keys(fieldsError).some(field => fieldsError[field])
}


export class RoleForm extends React.Component {
  constructor(props) {
    super(props)
    this.roles = null
    this.state = {value:undefined}
  }
  componentDidMount() {
    // To disabled submit button at the beginning.
    this.props.form.validateFields()
  }

  handleSubmit = async (e) => {
    e.preventDefault()
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.onSubmit()
        console.log(values)
        // edit
        axios.post('/api/v1/add_role', values)
          .then(resp => {
            message.success('成功添加')
          })
          .catch(err => {
            message.error(`添加失败，错误：${err}`)
          })
      }
    })
  }
  handChange = ()=>{
    this.setState({value:this.props.form.getFieldValue('level')})
    console.log(this.state.value)
  }
  render() {
    const {
      getFieldDecorator, getFieldsError, getFieldError, isFieldTouched
    } = this.props.form

    // Only show error after a field is touched.
    const roleError = isFieldTouched('role') && getFieldError('role')
    const descriptionError = isFieldTouched('description') && getFieldError('description')
    const levelError = isFieldTouched('level') && getFieldError('level')
    const permissionError = isFieldTouched('permission') && getFieldError('permission')
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Item
          {...FormItemLayout}
          validateStatus={roleError ? 'error' : ''}
          help={roleError || ''}
          label='角色'
        >
            {getFieldDecorator('role', {
            rules: [{ required: true, message: '请输入角色名!' }],
          })(
              <Input placeholder="请输入角色名" />
          )}
        </Form.Item>
         <Form.Item
          {...FormItemLayout}
          validateStatus={levelError ? 'error' : ''}
          help={levelError || ''}
          label='级别'
        >
            {getFieldDecorator('level', {
            rules: [{ required: true, message: '请选择角色级别!' }],
          })(
              <Select placeholder="请选择类型" onChange={this.handChange}>
                <Option key={0} value={0}>会员</Option>
                <Option key={1} value={1}>管理员</Option>
              </Select>
          )}
        </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={descriptionError ? 'error' : ''}
          help={descriptionError || ''}
          label='说明'
        >
            {getFieldDecorator('description', {
            rules: [{ required: true, message: '请输入说明!' }],
          })(
              <TextArea rows={4}  placeholder="请输入说明"/>
          )}
        </Form.Item>
        {
          this.state.value===0?(
          <Form.Item
            {...FormItemLayout}
            validateStatus={permissionError ? 'error' : ''}
            help={permissionError || ''}
            label='权限'
          >
            {getFieldDecorator('permission', {
            rules: [{ required: true, message: '请选择权限' }],
          })(<Select
              mode="multiple"
              placeholder="请选择权限"
              defaultValue={[0x02, 0x01]}
              >
                <Option key={0x01} value={0x01}>商品购买</Option>
                <Option key={0x02} value={0x02}>账单管理</Option>
                <Option key={0x04} value={0x04}>会员管理</Option>
                <Option key={0x08} value={0x08}>权限管理</Option>
                <Option key={0x10} value={0x10}>商品管理</Option>
              </Select>
              )
            }
          </Form.Item>):(<div> </div>)
          }
        <Form.Item {...FormItemLayoutWithOutLabel}>
          <Button
            type="primary"
            htmlType="submit"
            disabled={hasErrors(getFieldsError()
            )}
          >
            提交
          </Button>
        </Form.Item>
      </Form>
    )
  }
}

export default Form.create()(RoleForm)


