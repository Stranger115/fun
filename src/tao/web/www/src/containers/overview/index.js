'use strict'

import React from 'react'
import welcome from '../../static/welcome.png'

export default class Overview extends React.Component {
  render() {
    return <img src={welcome} height="735" width="137"/>
  }
}
