'use strict'

import React from 'react'
import { Icon } from 'antd'
import { Link } from 'react-router-dom'


const CustomIcon = ({type, color}) =>
  <Icon
    style={{fontSize: '1.5em', padding: '1px'}}
    type={type}
    theme='twoTone'
    twoToneColor={color}
  />

const PendingIcon = () => <CustomIcon type='clock-circle' color='#1890ff' />
const SuccessIcon = () => <CustomIcon type='check-circle' color='#52c41a' />
const SkippedIcon = () => <CustomIcon type='stop' color='#bfbfbf' />
const RunningIcon = () => <CustomIcon type='pause-circle' color='#faad14' />
const FailedIcon = () => <CustomIcon type='close-circle' color='#eb2f96' />

const IconText = ({ type, text, url }) => (
  <span>
    {
      url.startsWith('/') ?
        <Link to={url}>
          <Icon type={type} style={{ marginRight: 8 }} />
          {text}
        </Link> :
        <a href={url} target='_blank'>
          <Icon type={type} style={{ marginRight: 8 }} />
          {text}
        </a>
    }
  </span>
)


export {
  PendingIcon,
  SuccessIcon,
  SkippedIcon,
  FailedIcon,
  RunningIcon,
  IconText,
}
