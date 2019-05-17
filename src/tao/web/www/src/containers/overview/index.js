'use strict'

import React from 'react'
import welcome from '../../static/welcome.png'

export default class Overview extends React.Component {
  render() {
    return <img src={welcome} width="735" height="137"/>
  }
}
