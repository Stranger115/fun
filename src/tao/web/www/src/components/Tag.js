import React, { Component } from 'react'
import _ from 'lodash'
import { Input, Tag, Icon } from 'antd'


class EditableTagGroup extends Component {
  constructor(props) {
    super(props)
    this.state = {
      tags: props.tags || [],
      inputVisible: false,
      inputValue: '',
    }

    this.onUpdate = props.onUpdate
    this.newText = props.newText
  }

  componentWillReceiveProps(nextProps) {
    if (_.isEqual(this.props, nextProps)) {
      return
    }
    this.setState({tags: nextProps.tags || []})
  }

  handleClose = (removedTag) => {
    const tags = this.state.tags.filter(tag => tag !== removedTag)
    this.setState({ tags })
    this.onUpdate(tags)
  }

  showInput = () => {
    this.setState({ inputVisible: true }, () => this.input.focus())
  }

  handleInputChange = (e) => {
    this.setState({ inputValue: e.target.value })
  }

  handleInputConfirm = () => {
    const { inputValue } = this.state
    let { tags } = this.state
    if (inputValue && tags.indexOf(inputValue) === -1) {
      tags = [...tags, inputValue]
    }
    this.setState({
      tags,
      inputVisible: false,
      inputValue: '',
    })
    this.onUpdate(tags)
  }

  saveInputRef = input => this.input = input

  render() {
    const { tags, inputVisible, inputValue } = this.state
    return (
      <div>
        {tags.map((tag) => {
          const tagElem = (
            <Tag key={tag} closable={true} afterClose={() => this.handleClose(tag)}>
              {tag}
            </Tag>
          );
          return tagElem
        })}
        {inputVisible && (
          <Input
            ref={this.saveInputRef}
            type="text"
            size="small"
            style={{ width: 78 }}
            value={inputValue}
            onChange={this.handleInputChange}
            onBlur={this.handleInputConfirm}
            onPressEnter={this.handleInputConfirm}
          />
        )}
        {!inputVisible && (
          <Tag
            onClick={this.showInput}
            style={{ background: '#fff', borderStyle: 'dashed' }}
          >
            <Icon type="plus" /> {this.newText}
          </Tag>
        )}
      </div>
    )
  }
}


export { EditableTagGroup }
